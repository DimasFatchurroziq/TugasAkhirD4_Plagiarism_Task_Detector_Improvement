from fastapi.templating import Jinja2Templates
from src.utils.template_filters import register_filters

templates = Jinja2Templates(directory="src/templates")

register_filters(templates)