from starlette.templating import Jinja2Templates
import jinja2
import markdown
import html
import bleach

allowed_tags = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "pre",
    "strong",
    "ul",
    "h1",
    "h2",
    "h3",
    "p",
    "br",
    "ins",
    "del",
]

templates = Jinja2Templates(directory="templates")
templates.env.filters["markdown"] = lambda text: jinja2.Markup(
    bleach.clean(
        markdown.markdown(
            text,
            extensions=["markdown.extensions.fenced_code"],
        ),
        tags=allowed_tags,
    )
)
