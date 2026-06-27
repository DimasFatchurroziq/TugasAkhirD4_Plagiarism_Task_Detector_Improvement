from src.core.templates import templates
from fastapi import APIRouter, Request, Depends
from src.api.v1.dependencies import get_job_service, get_compare_service

router    = APIRouter()

@router.get("/", name="dashboard")
async def dashboard(request: Request, compare_service = Depends(get_compare_service), service = Depends(get_job_service)):
    jobs  = await service.get_latest_jobs()
    stats = await compare_service.get_stats()
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request":      request,
            "active_page":  "dashboard",
            "page_title":   "Dashboard",
            "jobs":         jobs,   # tampilkan 3 job terbaru
            "stats":        stats,
        },
    )
