from fastapi import FastAPI
from src.api.v1.routers.job_router import job_router
from src.api.v1.routers.document_router import document_router 
from src.api.v1.routers.comparison_router import comparison_router 
from src.api.v1.routers.process_router import process_router 

from src.api.v1.views import dashboard, jobs, upload, results, report, documents

# from src.utils.template_filters import register_filters

# from fastapi.templating import Jinja2Templates


from fastapi.staticfiles import StaticFiles

app = FastAPI()


# ── Static files ──────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# ── Template filters ──────────────────────────────────────────────
# templates = Jinja2Templates(directory="src/templates")
# register_filters(templates)

app.include_router(job_router)
app.include_router(document_router)
app.include_router(comparison_router)


app.include_router(dashboard.router)
app.include_router(jobs.router)
app.include_router(upload.router)
app.include_router(results.router)
app.include_router(report.router)
app.include_router(documents.router)

app.include_router(process_router)
