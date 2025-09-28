import secrets
import structlog

from sqlalchemy import func, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response, status
)


from tevye_gpt_server.src.db.client import get_db
from tevye_gpt_server.src.interfaces.auth import RegisterIn, TokenOut, LoginIn
from tevye_gpt_server.src.controllers.auth_controller import (
    set_refresh_cookie,
    get_refresh_from_request,
    clear_refresh_cookie
)
from tevye_gpt_server.src.modules.auth import (
    RoleEnum,
    RefreshSession,
    Tenant,
    User
)
from tevye_gpt_server.src.utils.app_security import (
    hash_password,
    make_access_token,
    make_refresh_token,
    hash_refresh,
    verify_password,
    decode_access_token,
    REFRESH_TTL, ACCESS_TTL
)

router = APIRouter(prefix='/auth', tags=['auth'])
log = structlog.get_logger(__name__='auth_routes')


def _roles_claim(user: User) -> list[str]:
    if hasattr(user, 'roles') and isinstance(user.roles, (list, tuple)):
        return [r.value if hasattr(r, 'value') else str(r) for r in user.roles]  # noqa: E501
    if hasattr(user, 'role'):
        r = user.role
        return [r.value if hasattr(r, 'value') else str(r)]
    return ['user']


def _utcnow():
    return datetime.now(timezone.utc)


@router.post('/login', response_model=TokenOut, status_code=status.HTTP_200_OK)
def login(data: LoginIn, request: Request,
          response: Response, db: Session = Depends(get_db)):
    email_norm = data.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email_norm).first()

    if not user:
        raise HTTPException(status_code=401,
                            detail='Invalid email or password')

    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(status_code=403, detail='User is inactive')

    if not verify_password(data.password, user.pwd_hash):
        raise HTTPException(status_code=401,
                            detail='Invalid email or password')

    fp = request.headers.get('User-Agent', 'unknown')[:255] or 'unknown'
    ip = request.client.host if request.client else None

    refresh, meta = make_refresh_token(sub=str(user.id), sid='pending')

    sess = RefreshSession(
        user_id=user.id,
        user_agent_fingerprint=fp,
        ip=ip,
        is_active=True,
        expires_at=_utcnow() + REFRESH_TTL,
        refresh_hash=hash_refresh(refresh),
        jti=meta['jti']
    )

    db.add(sess)
    db.flush()

    access = make_access_token(
        sub=str(user.id),
        sid=str(sess.id),
        roles=_roles_claim(user),
        token_version=user.token_version
    )

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        log.error('DB error on login commit', error=str(e))
        raise HTTPException(status_code=409, detail='Could not create session')

    set_refresh_cookie(response, refresh, int(REFRESH_TTL.total_seconds()))
    response.headers['X-CSRF-Issued'] = secrets.token_urlsafe(20)

    return TokenOut(access_token=access,
                    expires_in=int(ACCESS_TTL.total_seconds()))


@router.post("/refresh", response_model=TokenOut,
             status_code=status.HTTP_200_OK)
def refresh_token(request: Request, response: Response,
                  db: Session = Depends(get_db)):
    raw = get_refresh_from_request(request)
    if not raw:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    h = hash_refresh(raw)
    sess = (
        db.query(RefreshSession)
          .filter(RefreshSession.refresh_hash == h,
                  RefreshSession.is_active.is_(True))
          .first()
    )
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if sess.expires_at <= _utcnow():
        sess.is_active = False
        db.commit()
        clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="Refresh expired")

    user = db.query(User).get(sess.user_id)
    if not user or (hasattr(user, "is_active") and not user.is_active):
        sess.is_active = False
        db.commit()
        clear_refresh_cookie(response)
        raise HTTPException(status_code=403, detail="User disabled")

    new_refresh, meta = make_refresh_token(sub=str(user.id), sid=str(sess.id))
    sess.refresh_hash = hash_refresh(new_refresh)
    sess.jti = meta["jti"]
    sess.expires_at = _utcnow() + REFRESH_TTL

    access = make_access_token(
        sub=str(user.id),
        sid=str(sess.id),
        roles=_roles_claim(user),
        token_version=user.token_version,
    )

    db.commit()

    set_refresh_cookie(response, new_refresh,
                       max_age=int(REFRESH_TTL.total_seconds()))
    response.headers["X-CSRF-Issued"] = secrets.token_urlsafe(20)

    return TokenOut(access_token=access,
                    expires_in=int(ACCESS_TTL.total_seconds()))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response,
           db: Session = Depends(get_db)):
    raw = get_refresh_from_request(request)
    if not raw:
        clear_refresh_cookie(response)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    h = hash_refresh(raw)
    sess = (
        db.query(RefreshSession)
          .filter(RefreshSession.refresh_hash == h,
                  RefreshSession.is_active.is_(True))
          .first()
    )
    if sess:
        sess.is_active = False
        sess.expires_at = _utcnow()
        db.commit()

    clear_refresh_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout_all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all(request: Request, response: Response,
               db: Session = Depends(get_db)):
    """
    Requires Authorization: Bearer <access>.
    Invalidate ALL user's sessions and increase token_version,
    revoking all access tokens issued before.
    """

    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing access token")
    token = auth.split(" ", 1)[1].strip()

    try:
        claims = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid access token")

    # Invalida todas as sessões do user
    db.execute(
        update(RefreshSession)
        .where(RefreshSession.user_id == int(user_id),
               RefreshSession.is_active.is_(True))
        .values(is_active=False, expires_at=_utcnow())
    )
    # Bump de token_version
    user = db.query(User).get(int(user_id))
    if user:
        user.token_version = int(getattr(user, "token_version", 0)) + 1
    db.commit()

    clear_refresh_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    exists = db.query(User).filter(func.lower(User.email) == email_norm).first()  # noqa: E501
    if exists:
        raise HTTPException(status_code=409,
                            detail='Email already registered')

    pwd_hash = hash_password(data.password)

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
    refresh, meta = make_refresh_token(
        sub=str(user.id),
        sid="pending"
    )

    sess = RefreshSession(
        user_id=user.id,
        user_agent_fingerprint=fp,
        ip=ip,
        is_active=True,
        expires_at=datetime.now(timezone.utc) + REFRESH_TTL,
        refresh_hash=hash_refresh(refresh),
        jti=meta['jti']
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
    db.commit()

    set_refresh_cookie(response, refresh)
    response.headers['X-CSRF-Issued'] = secrets.token_urlsafe(20)

    return TokenOut(
        access_token=access,
        expires_in=int(ACCESS_TTL.total_seconds())
    )
