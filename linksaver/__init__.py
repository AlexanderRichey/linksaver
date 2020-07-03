from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from .handlers import (
    home,
    signup,
    create_user,
    login,
    create_session,
    logout,
    Items,
    ItemDetail,
)
from .auth import CookieAuthBackend
from .db import client


app = Starlette(
    debug=True,
    on_shutdown=[client.close],
    middleware=[
        Middleware(
            SessionMiddleware, secret_key="mysecret", session_cookie="session_id"
        ),
        Middleware(AuthenticationMiddleware, backend=CookieAuthBackend()),
    ],
    routes=[
        Route("/", home, methods=["GET", "POST"]),
        Route("/signup", signup, methods=["GET"]),
        Route("/register", create_user, methods=["POST"]),
        Route("/login", login, methods=["GET"]),
        Route("/sessions", create_session, methods=["POST"]),
        Route("/logout", logout, methods=["GET"]),
        Route("/items", Items),
        Route("/items/{item_id}", ItemDetail),
    ],
)
