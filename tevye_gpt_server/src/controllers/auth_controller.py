import os

from fastapi import Response


def set_refresh_cookie(resp: Response, token: str):
    resp.set_cookie(
        key=os.getenv('REFRESH_COOKIE_NAME', 'refresh_token'),
        value=token,
        httponly=True,
        secure=True,
        samesite='lax',
        path='auth/refresh',
        domain=os.getenv('SECURE_COOKIE_DOMAIN')
    )
