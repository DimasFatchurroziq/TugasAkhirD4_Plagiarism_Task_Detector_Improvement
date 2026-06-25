"""
app/routers/report.py
"""

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from src.services import job_service

router    = APIRouter(prefix="/report")
templates = Jinja2Templates(directory="templates")


@router.get("/", name="report_page")
async def report_page(request: Request):
    jobs = job_service.get_all_jobs()
    return templates.TemplateResponse(
        "pages/report.html",
        {
            "request":     request,
            "active_page": "report",
            "page_title":  "Buat Laporan",
            "jobs":        jobs,
            "methods":     ["Cosine Similarity (TF-IDF)", "Jaccard Similarity",
                            "Fingerprinting (Winnowing)", "Levenshtein Distance", "SimHash"],
        },
    )


@router.post("/generate", name="report_generate")
async def report_generate(
    job_id:    int  = Form(...),
    format:    str  = Form(default="xlsx"),
    threshold: int  = Form(default=40),
    order:     str  = Form(default="sim_desc"),
    notes:     str  = Form(default=""),
):
    """
    Generate laporan.
    TODO: Implementasikan pembuatan PDF/Excel sungguhan di sini.
    """
    job   = job_service.get_job(job_id)
    pairs = job_service.get_pairs()
    filtered = [p for p in pairs if p.sim >= threshold]

    return JSONResponse({
        "ok":      True,
        "job":     job.name if job else "Unknown",
        "format":  format,
        "total":   len(filtered),
        "message": f"Laporan '{format.upper()}' untuk {len(filtered)} pasangan berhasil dibuat.",
    })
