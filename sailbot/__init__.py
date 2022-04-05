import os
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

from .handlers import (
    home,
    user_form,
    create_user,
    session_form,
    create_session,
    delete_session,
    notes,
    search,
    tags,
)
from .auth import CookieAuthBackend
from .db import client


app = Starlette(
    debug=os.getenv("DEBUG"),
    on_shutdown=[client.close],
    middleware=[Middleware(AuthenticationMiddleware, backend=CookieAuthBackend())],
    routes=[
        Route("/", home, methods=["GET"]),
        Route("/users", user_form, methods=["GET"]),
        Route("/users", create_user, methods=["POST"]),
        Route("/sessions", session_form, methods=["GET"]),
        Route("/sessions", create_session, methods=["POST"]),
        Route("/logout", delete_session, methods=["GET"]),
        Route("/notes", notes.render_form, methods=["GET"]),
        Route("/notes", notes.create_resource, methods=["POST"]),
        Route("/notes/{id}", notes.render_form, methods=["GET"]),
        Route("/notes/{id}/update", notes.update_resource, methods=["POST"]),
        Route("/notes/{id}/pin", notes.pin_resource, methods=["POST"]),
        Route("/notes/{id}/unpin", notes.unpin_resource, methods=["POST"]),
        Route("/notes/{id}/delete", notes.delete_resource, methods=["POST"]),
        Route("/tags/{tag}", tags, methods=["GET"]),
        Route("/search", search, methods=["GET"]),
        Mount("/", app=StaticFiles(directory="static")),
    ],
)
