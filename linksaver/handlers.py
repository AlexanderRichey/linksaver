from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, ValidationError, Field
from typing import Pattern
import bcrypt

from .templates import templates
from .models import User
from .forms import UserForm


async def home(request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": request.user}
    )


async def signup(request):
    if request.user.is_authenticated:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("signup.html", {"request": request})


@requires(["unauthenticated"])
async def create_user(request):
    context = {
        "request": request,
        "user": request.user,
    }

    try:
        form_data = await request.form()
        user_form = UserForm(**dict(form_data))
    except ValidationError as e:
        for error in e.errors():
            context[error["loc"][0]] = error["msg"]
        return templates.TemplateResponse("signup.html", context)

    user = User.get_by_email(user_form.email)
    if user:
        context["email"] = "This email is already registered"
        return templates.TemplateResponse("signup.html", context)

    password_digest = bcrypt.hashpw(
        bytes(user_form.password, encoding="utf8"), bcrypt.gensalt()
    )
    user = User(email=user_form.email, password_digest=password_digest.decode("utf-8"))
    user.put()

    request.session.update(id=user.session_id)

    return RedirectResponse(url="/")


async def login(request):
    if request.user.is_authenticated:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("login.html", {"request": request})


@requires(["unauthenticated"])
async def create_session(request):
    context = {
        "request": request,
        "user": request.user,
        "password": "Invalid credentials",
    }

    try:
        form_data = await request.form()
        user_form = UserForm(**dict(form_data))
    except ValidationError as e:
        for error in e.errors():
            context[error["loc"][0]] = error["msg"]
        return templates.TemplateResponse("login.html", context)

    user = User.get_by_email(user_form.email)
    if not user:
        return templates.TemplateResponse("login.html", context)

    if bcrypt.checkpw(
        bytes(user_form.password, encoding="utf8"),
        bytes(user.password_digest, encoding="utf8"),
    ):
        request.session.update(id=user.session_id)
        return RedirectResponse(url="/")

    return templates.TemplateResponse("login.html", context)


async def logout(request):
    request.session.pop("id", None)
    return RedirectResponse(url="/")


class Items(HTTPEndpoint):
    pass


class ItemDetail(HTTPEndpoint):
    pass
