import os

from fastapi import Response, Request


def set_refresh_cookie(resp: Response, token: str, max_age: int | None = None):
    resp.set_cookie(
        key=os.getenv('REFRESH_COOKIE_NAME', 'refresh_token'),
        value=token,
        httponly=True,
        secure=True,
        samesite='lax',
        path='auth/refresh',
        domain=os.getenv('SECURE_COOKIE_DOMAIN'),
        max_age=max_age
    )


def clear_refresh_cookie(resp: Response):
    resp.delete_cookie(
        key=os.getenv('REFRESH_COOKIE_NAME', 'refresh_token'),
        path='auth/refresh'
    )


def get_refresh_from_request(req: Request) -> str | None:
    return req.cookies.get(os.getenv('REFRESH_COOKIE_NAME', 'refresh_token'))
