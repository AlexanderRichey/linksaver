from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.responses import RedirectResponse, JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException
from pydantic import BaseModel, EmailStr, ValidationError, Field
from typing import Pattern
import bcrypt

from .templates import templates
from .models import User, Item, TYPE_NOTE, TYPE_LINK
from .forms import UserForm, NoteForm, LinkForm, ApiLinkForm
from .magic import csrf_signer


async def home(request):
    context = {"request": request, "user": request.user}
    if request.user.is_authenticated:
        items = Item.get_by_user(request.user)
        context["items"] = items
    return templates.TemplateResponse("index.html", context)


async def user_form(request):
    if request.user.is_authenticated:
        return RedirectResponse(url="/")
    context = {"request": request, "user": request.user}
    return templates.TemplateResponse("signup.html", context)


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
        return templates.TemplateResponse("signup.html", context, 400)

    user = User.get_by_email(user_form.email)
    if user:
        context["email"] = "This email is already registered"
        return templates.TemplateResponse("signup.html", context, 400)

    password_digest = bcrypt.hashpw(
        bytes(user_form.password, encoding="utf8"), bcrypt.gensalt()
    )
    user = User(email=user_form.email, password_digest=password_digest.decode("utf-8"))
    user.put()

    resp = RedirectResponse(url="/")
    resp.set_cookie("session_id", user.session_id, max_age=31556952, httponly=True)

    return resp


async def session_form(request):
    if request.user.is_authenticated:
        return RedirectResponse(url="/")
    context = {"request": request, "user": request.user}
    return templates.TemplateResponse("login.html", context)


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
        return templates.TemplateResponse("login.html", context, 400)

    user = User.get_by_email(user_form.email)
    if not user:
        return templates.TemplateResponse("login.html", context, 400)

    if bcrypt.checkpw(
        bytes(user_form.password, encoding="utf8"),
        bytes(user.password_digest, encoding="utf8"),
    ):
        resp = RedirectResponse(url="/")
        resp.set_cookie("session_id", user.session_id, max_age=31556952, httponly=True)
        return resp

    return templates.TemplateResponse("login.html", context)


async def delete_session(request):
    if request.user.is_authenticated:
        request.user.roll_session()
        request.user.put()
    resp = RedirectResponse(url="/")
    resp.delete_cookie("session_id")
    return resp


@requires(["authenticated"])
async def note_form(request):
    return templates.TemplateResponse(
        "note.html",
        {
            "request": request,
            "user": request.user,
            "csrf": csrf_signer.sign(request.user.session_id).decode("utf-8"),
        },
    )


@requires(["authenticated"])
async def create_note(request):
    context = {
        "request": request,
        "user": request.user,
    }

    try:
        form_data = await request.form()
        note_form = NoteForm(**dict(form_data))
    except ValidationError as e:
        for error in e.errors():
            context[error["loc"][0]] = error["msg"]
        return templates.TemplateResponse("note.html", context, 400)

    if not csrf_signer.validate(note_form.csrf):
        raise HTTPException(401)

    item = Item(
        email=request.user.email,
        type=TYPE_NOTE,
        title=note_form.title,
        body=note_form.body,
    )
    item.put()

    return RedirectResponse(url="/")


@requires(["authenticated"])
async def link_form(request):
    return templates.TemplateResponse(
        "link.html",
        {
            "request": request,
            "user": request.user,
            "csrf": csrf_signer.sign(request.user.session_id).decode("utf-8"),
        },
    )


@requires(["authenticated"])
async def create_link(request):
    context = {
        "request": request,
        "user": request.user,
    }

    try:
        form_data = await request.form()
        link_form = LinkForm(**{k: v for k, v in dict(form_data).items() if v != ""})
    except ValidationError as e:
        for error in e.errors():
            context[error["loc"][0]] = error["msg"]
        return templates.TemplateResponse("link.html", context, 400)

    if not csrf_signer.validate(link_form.csrf):
        raise HTTPException(401)

    item = Item(
        email=request.user.email,
        type=TYPE_LINK,
        title=link_form.title,
        body=link_form.body,
        url=link_form.url,
        favicon=link_form.favicon,
    )
    item.put()

    return RedirectResponse(url="/")


async def api_create_link(request):
    if request.method == "OPTIONS":
        return PlainTextResponse(
            headers={
                "access-control-allow-headers": "Authorization,Content-Type",
                "access-control-allow-origin": "*",
            },
        )

    auth = request.headers["authorization"]
    try:
        scheme, token = auth.split()
        if scheme.lower() != "bearer":
            return JSONResponse({"message": "unauthorized"}, status_code=401)
    except ValueError:
        return JSONResponse({"message": "unauthorized"}, status_code=401)

    user = User.get_by_token(token)
    if not user:
        return JSONResponse({"message": "unauthorized"}, status_code=401)

    try:
        json_body = await request.json()
        link_form = ApiLinkForm(**{k: v for k, v in dict(json_body).items() if v != ""})
    except ValidationError as e:
        errors = {}
        for error in e.errors():
            errors[error["loc"][0]] = error["msg"]
        return JSONResponse(
            errors, status_code=400, headers={"access-control-allow-origin": "*",}
        )

    item = Item(
        email=user.email,
        type=TYPE_LINK,
        title=link_form.title,
        url=link_form.url,
        favicon=link_form.favicon,
    )
    item.put()

    return JSONResponse(
        item.json(), status_code=201, headers={"access-control-allow-origin": "*",}
    )
