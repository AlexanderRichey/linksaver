from starlette.authentication import requires
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from pydantic import ValidationError

from .templates import templates
from .magic import csrf_signer


class HandlerFactory:
    def __init__(self, resource_type, resource, resource_form, template):
        self.resource_type = resource_type
        self.resource_form = resource_form
        self.resource = resource
        self.template = template

    def get_resource(self, request):
        resource_id = request.path_params.get("id")
        resource = self.resource.get_by_id(resource_id)
        if not resource:
            raise HTTPException(404)
        if resource.email != request.user.email:
            raise HTTPException(401)
        return resource

    @requires(["authenticated"])
    def render_form(self, request):
        context = {
            "request": request,
            "user": request.user,
            "csrf": csrf_signer.sign(request.user.session_id).decode("utf-8"),
        }

        if request.path_params.get("id"):
            resource = self.get_resource(request)
            context[self.resource_type] = resource
            context["action"] = f"/{self.resource_type}s/{resource.id}/update"
        else:
            context[self.resource_type] = None
            context["action"] = f"/{self.resource_type}s"

        return templates.TemplateResponse(self.template, context)

    @requires(["authenticated"])
    async def create_resource(self, request):
        context = {
            "request": request,
            "user": request.user,
        }

        form_data = await request.form()
        clean_form_data = {k: v for k, v in form_data.items() if v}

        try:
            form = self.resource_form(**dict(clean_form_data))
        except ValidationError as e:
            for error in e.errors():
                context[error["loc"][0]] = error["msg"]
            context[self.resource_type] = clean_form_data
            return templates.TemplateResponse(self.template, context, 400)

        if not csrf_signer.validate(form.csrf):
            raise HTTPException(401)

        item = self.resource(
            email=request.user.email, type=self.resource_type, **dict(form)
        )
        item.put()

        return RedirectResponse(url="/", status_code=302)

    @requires(["authenticated"])
    async def update_resource(self, request):
        resource = self.get_resource(request)
        context = {
            "request": request,
            "user": request.user,
        }

        try:
            form_data = await request.form()
            form = self.resource_form(
                **dict({k: v for k, v in form_data.items() if v})
            )
        except ValidationError as e:
            for error in e.errors():
                context[error["loc"][0]] = error["msg"]
            return templates.TemplateResponse(self.template, context, 400)

        if not csrf_signer.validate(form.csrf):
            raise HTTPException(401)

        for k, v in dict(form).items():
            if hasattr(resource, k):
                setattr(resource, k, v)

        resource.put()

        return RedirectResponse(url="/", status_code=302)

    @requires(["authenticated"])
    async def pin_resource(self, request):
        resource = self.get_resource(request)
        context = {
            "request": request,
            "user": request.user,
        }
        resource.is_pin = True
        resource.put()
        return RedirectResponse(url="/", status_code=302)

    @requires(["authenticated"])
    async def unpin_resource(self, request):
        resource = self.get_resource(request)
        context = {
            "request": request,
            "user": request.user,
        }
        resource.is_pin = False
        resource.put()
        return RedirectResponse(url="/", status_code=302)

    def delete_resource(self, request):
        resource = self.get_resource(request)
        resource.delete()
        return RedirectResponse(url="/", status_code=302)
