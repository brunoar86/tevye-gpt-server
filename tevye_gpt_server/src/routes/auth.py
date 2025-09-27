import secrets
import structlog

from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response, status
)
from security import (
    bcrypt,
    make_access_token,
    make_refresh_token,
    hash_refresh,
    REFRESH_TTL, ACCESS_TTL
)

from tevye_gpt_server.src.db.client import db_client
from tevye_gpt_server.src.interfaces.auth import RegisterIn, TokenOut
from tevye_gpt_server.src.modules.auth import (
    RoleEnum,
    RefreshSession,
    Tenant,
    User
)
from tevye_gpt_server.src.controllers.auth_controller import set_refresh_cookie

router = APIRouter(prefix='/auth', tags=['auth'])
get_db = db_client.get_db
log = structlog.get_logger(__name__='register route')


@router.post('/register', response_model=TokenOut,
             status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterIn, request: Request,
                  response: Response, db: Session = Depends(get_db)):
    tenant_id = None
    if data.tenant_name:
        tenant = db.query(Tenant).filter(func.lower(Tenant.name) == data.tenant_name.strip().lower()).first()  # noqa: E501
        if not tenant:
            tenant = Tenant(name=data.tenant_name.strip())
            db.add(tenant)
            db.flush()
        tenant_id = tenant.id

    email_norm = data.email.strip().lower()
    exists = db.query(User.filter(func.lower(User.email) == email_norm).first())  # noqa: E501
    if exists:
        raise HTTPException(status_code=409, detail='Email already registered')  # noqa: E501

    pwd_hash = bcrypt.hash(data.password)

    user = User(
        email=email_norm,
        pwd_hash=pwd_hash,
        roles=[RoleEnum.user],
        tenant_id=tenant_id
    )
    db.add(user)
    db.flush()

    fp = 'register'
    ip = request.client.host if request.client else None

    sess = RefreshSession(
        user_id=user.id,
        user_agent_fingerprint=fp,
        ip=ip,
        is_active=True,
        expires_at=datetime.now(timezone.utc) + REFRESH_TTL
    )
    db.add(sess)
    db.flush()

    access = make_access_token(
        sub=str(user.id),
        sid=str(sess.id),
        roles=[r.value for r in user.roles],
        token_version=user.token_version
    )
    refresh, meta = make_refresh_token(
        sub=str(user.id),
        sid=str(sess.id)
    )
    sess.refresh_hash = hash_refresh(refresh)
    sess.jti = meta['jti']
    db.commit()

    set_refresh_cookie(response, refresh)
    response.headers['X-CSRF-Issued'] = secrets.token_urlsafe(20)

    return TokenOut(
        access_token=access,
        expires_in=int(ACCESS_TTL.total_seconds())
    )
