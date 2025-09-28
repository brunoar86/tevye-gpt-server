import re

from pydantic import BaseModel, EmailStr, field_validator, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    tenant_name: str | None = None

    @field_validator('password')
    @classmethod
    def strong_password(cls, v: str) -> str:
        if len(v) < 8 or not re.search(r'[A-Z]', v) or not re.search(r'[a-z]', v) or not re.search(r'\d', v):  # noqa: E501
            raise ValueError('Password must be at least 8 characters long, \
                             contain at least one uppercase letter, one \
                             lowercase letter, and one digit.')
        return v


class TokenOut(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    expires_in: int


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
