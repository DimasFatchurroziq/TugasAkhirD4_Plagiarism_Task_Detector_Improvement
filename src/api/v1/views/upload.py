"""
app/routers/upload.py
"""
from src.core.templates import templates

from uuid import UUID, uuid4

import os
import uuid
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from src.services import job_service, dashboard_service
from src.api.v1.dependencies import get_job_service, get_compare_service, get_doc_service

router    = APIRouter(prefix="/upload")
# templates = Jinja2Templates(directory="templates")

ALLOWED_EXTS  = {"pdf", "docx", "txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024   # 10 MB
UPLOAD_DIR    = "uploads"           # folder penyimpanan file


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", name="upload_page")
async def upload_page(
    request: Request, 
    job_id: UUID | None = None, # Menggunakan type hint yang konsisten dengan router sebelah
    compare_service = Depends(get_compare_service), 
    service = Depends(get_job_service) # Di router sebelah kamu pakai nama 'job_service', sesuaikan jika perlu
):
    stats = await compare_service.get_stats()
    jobs = await service.get_all_jobs()
    job = None
    
    if job_id:
        job = await service.get_job(job_id)

    if not job and jobs:
        job = jobs[-1]
        job_id = job.id  # Update job_id agar variabel ID ikut menyesuaikan

    return templates.TemplateResponse(
        "pages/upload.html",
        {
            "request":         request,
            "active_page":    "upload",
            "page_title":     "Upload File",
            "jobs":           jobs,
            "selected_job_id": job_id,
            "job":             job, # Menggunakan nama variabel "job" agar konsisten dengan router sebelah
            "stats":          stats,
        },
    )


@router.post("/files", name="upload_files")
async def upload_files(
    request: Request,
    job_id:  UUID            = Form(...),
    files:   list[UploadFile] = File(...),
    category: str = Form(default="MANY"),
    doc_service = Depends(get_doc_service),
    job_service = Depends(get_job_service),
):
    """
    Upload satu atau beberapa file ke job tertentu.
    Kembalikan JSON { uploaded: [...], errors: [...] }
    """
    # print(files)
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job tidak ditemukan")

    # _ensure_upload_dir()
    uploaded = []
    errors   = []

    result = await doc_service.create_job_documents(job_id, files, category, UPLOAD_DIR)

    return JSONResponse({
        "job_id": str(job_id),
        "created": result["created"],
        "uploaded": [
            {
                "id": str(doc.id),
                "name": doc.name,
                "path": doc.path
            }
            for doc in result["documents"]
        ],
        "errors": []
    })
