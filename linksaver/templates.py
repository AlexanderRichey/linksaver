from starlette.templating import Jinja2Templates
import jinja2
import markdown

md = markdown.Markdown()

templates = Jinja2Templates(directory="templates")
templates.env.filters["markdown"] = lambda text: jinja2.Markup(md.convert(text))
