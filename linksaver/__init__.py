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
    links,
    notes,
    api_create_link,
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
        Route("/links", links.render_form, methods=["GET"]),
        Route("/links", links.create_resource, methods=["POST"]),
        Route("/links/{id}", links.render_form, methods=["GET"]),
        Route("/links/{id}/update", links.update_resource, methods=["POST"]),
        Route("/links/{id}/delete", links.delete_resource, methods=["POST"]),
        Route("/notes", notes.render_form, methods=["GET"]),
        Route("/notes", notes.create_resource, methods=["POST"]),
        Route("/notes/{id}", notes.render_form, methods=["GET"]),
        Route("/notes/{id}/update", notes.update_resource, methods=["POST"]),
        Route("/notes/{id}/delete", notes.delete_resource, methods=["POST"]),
        Route("/api/links", api_create_link, methods=["POST", "OPTIONS"]),
    ],
)
