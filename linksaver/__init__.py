from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

from .handlers import (
    home,
    user_form,
    create_user,
    session_form,
    create_session,
    delete_session,
    note_form,
    create_note,
)
from .auth import CookieAuthBackend
from .db import client


app = Starlette(
    debug=True,
    on_shutdown=[client.close],
    middleware=[Middleware(AuthenticationMiddleware, backend=CookieAuthBackend())],
    routes=[
        Route("/", home, methods=["GET", "POST"]),
        Route("/users", user_form, methods=["GET"]),
        Route("/users", create_user, methods=["POST"]),
        Route("/sessions", session_form, methods=["GET"]),
        Route("/sessions", create_session, methods=["POST"]),
        Route("/logout", delete_session, methods=["GET"]),
        Route("/notes", note_form, methods=["GET"]),
        Route("/notes", create_note, methods=["POST"]),
    ],
)
