from src.core.templates import templates
from uuid import UUID
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, FileResponse
from src.services import job_service, dashboard_service

from src.api.v1.dependencies import get_compare_service, get_job_service, get_doc_service

router    = APIRouter(prefix="/documents")

@router.get("/", name="documents_page")
async def results_page(request: Request, job_id: UUID | None = None, filter: str = "all", compare_service = Depends(get_compare_service), job_service = Depends(get_job_service), doc_service = Depends(get_doc_service)):
    stats = await compare_service.get_stats()
    jobs  = await job_service.get_all_jobs()
    job = None
    
    if job_id:
        job = await job_service.get_job(job_id)

    if not job and jobs:
        job = jobs[-1]
        job_id = job.id  

    documents = []

    if job:
        job = await job_service.get_job(job_id)

        documents = await doc_service.get_all_job_documents(
            job_id=job_id,
        )

    all_pairs = []

    if job:
        all_pairs = await doc_service.get_pairs(
            job_id=job_id,
            filter_level="total"
        )

    status = [
        p.status or 0
        for p in all_pairs
    ]

    counts = {
        "processing": len([s for s in status if s == "PROCESSING"]),
        "done": len([s for s in status if s == "DONE"]),
        "error": len([s for s in status if s == "ERROR"]),
    }

    # print(comparisons)

    return templates.TemplateResponse(
        "pages/documents.html",
        {
            "request":        request,
            "active_page":    "f",
            "page_title":     "Documents",
            "job":            job,
            "jobs":           jobs,
            "comparisons":    documents,
            "counts":         counts,
            "stats":          stats,
        },
    )


@router.get("/{document_id}/view", name="view_full_document")
async def view_full_document(document_id: UUID, doc_service = Depends(get_doc_service)):
    document = await doc_service.get_document(document_id)
    
    if not document or not document.path:
        raise HTTPException(status_code=404, detail="Berkas dokumen tidak ditemukan")
        
    # Pastikan file fisik benar-to-benar ada di storage server
    import os
    if not os.path.exists(document.path):
        raise HTTPException(status_code=404, detail="Fisik dokumen hilang di server")

    return FileResponse(
        path=document.path,
        media_type="application/pdf"
    )

