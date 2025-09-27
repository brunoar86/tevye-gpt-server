from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from tevye_gpt_server.src.config.settings import settings


def _augment_dsn_with_ssl(dsn: str, sslmode: str | None) -> str:
    if not sslmode:
        return dsn

    sep = '&' if '?' in dsn else '?'
    return f"{dsn}{sep}sslmode={sslmode}"


raw_dsn: str = str(settings.DB_DSN)
dsn: str = _augment_dsn_with_ssl(settings.DB_DSN, settings.DB_SSLMODE)

engine = create_engine(
    raw_dsn,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
    future=True,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def healthcheck() -> bool:
    with engine.connect() as conn:
        conn.execute(text("SELECT * FROM users;"))
    return True
