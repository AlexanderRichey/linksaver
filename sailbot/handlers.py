from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.responses import RedirectResponse, JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException
from pydantic import BaseModel, EmailStr, ValidationError, Field
from typing import Pattern
import collections
import bcrypt
import urllib

from .templates import templates
from .models import User, Item, TYPE_NOTE, TYPE_LINK
from .forms import UserForm, NoteForm, LinkForm, ApiLinkForm
from .magic import csrf_signer
from .lib import HandlerFactory


notes = HandlerFactory(TYPE_NOTE, Item, NoteForm, "note.html")
links = HandlerFactory(TYPE_LINK, Item, LinkForm, "link.html")


def _get_page(request) -> int:
    page = request.query_params.get("page", 0)
    try:
        page = int(page)
    except ValueError:
        page = 0
    return abs(page)


async def home(request):
    context = {"request": request, "user": request.user}
    if request.user.is_authenticated:
        page = _get_page(request)
        filter = request.query_params.get("filter", "")
        search = request.query_params.get("search", "")

        items = Item.get_by_user(request.user, page, filter, search)
        days = collections.defaultdict(list)
        for item in items:
            days[item.created_at.strftime("%A %-d %B")].append(item)
        context["days"] = days

        pins = Item.get_pins_by_user(request.user)
        context["pins"] = pins

        context["page"] = page
        context["next_page"] = abs(page + 1)
        context["prev_page"] = max(page - 1, 0)
        context["search"] = search
    return templates.TemplateResponse("index.html", context)


@requires(["authenticated"])
async def tags(request):
    context = {"request": request, "user": request.user}
    page = _get_page(request)
    tag = request.path_params.get("tag")
    items = Item.get_by_user(request.user, page=page, tag=tag)
    context["items"] = items
    context["next_page"] = abs(page + 1)
    context["prev_page"] = max(page - 1, 0)
    context["tag"] = tag.title()
    return templates.TemplateResponse("tags.html", context)


async def oauth_form(request):
    redirect_uri = request.query_params.get("redirect_uri")

    if not redirect_uri:
        raise HTTPException(404)

    if request.user.is_authenticated:
        return RedirectResponse(url=f"{redirect_uri}?token={request.user.token}")
    context = {
        "request": request,
        "user": request.user,
        "heading_text": "Login",
        "page_title": "Login",
        "action": f"/oauth?redirect_uri={urllib.parse.quote(redirect_uri)}",
        "button_text": "Login",
        "auth": {"email": "", "password": ""},
    }
    return templates.TemplateResponse("oauth.html", context)


async def oauth(request):
    redirect_uri = request.query_params.get("redirect_uri")

    if not redirect_uri:
        raise HTTPException(404)

    context = {
        "request": request,
        "user": request.user,
        "heading_text": "Login",
        "page_title": "Login",
        "action": f"/oauth?redirect_uri={urllib.parse.quote(redirect_uri)}",
        "button_text": "Login",
        "password": "Invalid credentials",
        "auth": {"email": "", "password": ""},
    }

    form_data = await request.form()
    clean_form_data = {k: v for k, v in form_data.items() if v}
    context["auth"].update(clean_form_data)

    try:
        user_form = UserForm(**dict(form_data))
    except ValidationError as e:
        for error in e.errors():
            context[error["loc"][0]] = error["msg"]
        return templates.TemplateResponse("auth.html", context, 400)

    user = User.get_by_email(user_form.email)
    if not user:
        return templates.TemplateResponse("oauth.html", context, 400)

    if bcrypt.checkpw(
        bytes(user_form.password, encoding="utf8"),
        bytes(user.password_digest, encoding="utf8"),
    ):
        print(f"{redirect_uri}?token={user.token}")
        return RedirectResponse(
            url=f"{redirect_uri}?token={user.token}", status_code=302
        )

    return templates.TemplateResponse("oauth.html", context, 400)


async def user_form(request):
    if request.user.is_authenticated:
        return RedirectResponse(url="/", status_code=302)
    context = {
        "request": request,
        "user": request.user,
        "auth": {"email": "", "password": ""},
    }
    return templates.TemplateResponse("signup.html", context)


@requires(["unauthenticated"])
async def create_user(request):
    context = {
        "request": request,
        "user": request.user,
        "auth": {"email": "", "password": ""},
    }

    form_data = await request.form()
    clean_form_data = {k: v for k, v in form_data.items() if v}
    context["auth"].update(clean_form_data)

    try:
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
    user.put(create=True)

    resp = RedirectResponse(url="/", status_code=302)
    resp.set_cookie("session_id", user.session_id, max_age=31556952, httponly=True)

    return resp


async def session_form(request):
    if request.user.is_authenticated:
        return RedirectResponse(url="/", status_code=302)
    context = {
        "request": request,
        "user": request.user,
        "auth": {"email": "", "password": ""},
    }
    return templates.TemplateResponse("login.html", context)


@requires(["unauthenticated"])
async def create_session(request):
    context = {
        "request": request,
        "user": request.user,
        "password": "Invalid credentials",
        "auth": {"email": "", "password": ""},
    }

    form_data = await request.form()
    clean_form_data = {k: v for k, v in form_data.items() if v}
    context["auth"].update(clean_form_data)

    try:
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
        resp = RedirectResponse(url="/", status_code=302)
        resp.set_cookie("session_id", user.session_id, max_age=31556952, httponly=True)
        return resp

    return templates.TemplateResponse("login.html", context)


async def delete_session(request):
    if request.user.is_authenticated:
        request.user.roll_session()
        request.user.put()
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie("session_id")
    return resp


async def search(request):
    context = {"request": request, "user": request.user}
    return templates.TemplateResponse("search.html", context)


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
            errors,
            status_code=400,
            headers={
                "access-control-allow-origin": "*",
            },
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
        item.json(),
        status_code=201,
        headers={
            "access-control-allow-origin": "*",
        },
    )
