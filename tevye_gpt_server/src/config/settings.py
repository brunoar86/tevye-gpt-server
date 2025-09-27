from pydantic import BaseSettings, AnyUrl, Field


class PostgresDsn(AnyUrl):
    allowed_schemes = {'postgresql', 'postgres'}
    user_required = True


class Settings(BaseSettings):
    DB_DSN: PostgresDsn = Field(
        default="postgresql://postgres:postgres@localhost:5432/tevye_auth"
    )
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_PRE_PING: bool = True
    DB_SSLMODE: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
