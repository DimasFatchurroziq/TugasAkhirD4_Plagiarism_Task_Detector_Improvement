"""
app/routers/results.py
"""
from src.core.templates import templates

from uuid import UUID

import json

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from src.services import job_service, dashboard_service

from src.api.v1.dependencies import get_compare_service, get_job_service, get_doc_service, get_convert_service

router    = APIRouter(prefix="/results")


@router.get("/", name="results_page")
async def results_page(request: Request, job_id: UUID | None = None, filter: str = "all", view: str = "table", compare_service = Depends(get_compare_service), job_service = Depends(get_job_service)):
    stats = await compare_service.get_stats()
    jobs  = await job_service.get_all_jobs()
    job = None
    
    if job_id:
        job = await job_service.get_job(job_id)

    # 2. JIKA job_id KOSONG TAPI ADA DAFTAR JOBS, OTOMATIS AMBIL JOB PERTAMA
    if not job and jobs:
        job = jobs[-1]
        job_id = job.id  # Update job_id agar query di bawahnya ikut menyesuaikan

    comparisons = []

    if job:
        comparisons = await compare_service.get_pairs(
            job_id=job_id,
            filter_level=filter
        )

    all_pairs = []

    if job:
        all_pairs = await compare_service.get_pairs(
            job_id=job_id,
            filter_level="all"
        )

    if job:
        threshold = job.threshold 

    scores = [
        p.final_score or 0
        for p in all_pairs
    ]

    plagiat = [
        True if p.is_plagiat else False
        for p in all_pairs
    ]

    counts = {
        "all": len(scores),
        "plag": len([s for s in plagiat if s]),
        "high": len([s for s in scores if s >= threshold/100]),
        "med": len([s for s in scores if 0.4 <= s < threshold/100]),
        "low": len([s for s in scores if s < 0.4]),
    }


    # ── Data untuk heatmap.js ──────────────────────────────────
    # Kumpulkan semua nama file unik dari pairs
    files_set: set[str] = set()
    for p in all_pairs:
        files_set.add(p.document_1.name)
        files_set.add(p.document_2.name)
    files_list = sorted(files_set)  # urutan awal: alfabetis
    # print(files_list)

    # Serialisasi pairs ke JSON (hanya field yang dibutuhkan JS)
    pairs_json = json.dumps([
        {
            "id":     str(p.id),
            "file_a": p.document_1.name,
            "file_b": p.document_2.name,
            "sim": int((p.final_score or 0) * 100),
            # "status": p.status.value,
            # "note":   p.note,
            # "action": p.action,
        }
        for p in all_pairs
    ])

    # print(pairs_json)

    files_json = json.dumps(files_list)

    # print(comparisons)

    return templates.TemplateResponse(
        "pages/results.html",
        {
            "request":        request,
            "active_page":    "results",
            "page_title":     "Hasil Analisis",
            "job":            job,
            "jobs":           jobs,
            "comparisons":    comparisons,
            "threshold":      threshold,
            "counts":         counts,
            "active_filter":  filter,
            "view_mode":      view,              # ← BARU
            "max_sim":        max(scores, default=0),
            "high_count":     counts["high"],
            "total_files":    len(job.documents) if job else 0,
            "stats":          stats,

            # ← BARU: data untuk heatmap.js
            "pairs_json":     pairs_json,
            "files_json":     files_json,
        },
    )
    

@router.get("/pairs/{pair_id}", name="results_pair_detail")
async def pair_detail(request: Request, pair_id: UUID, threshold: int = 70, compare_service = Depends(get_compare_service), job_service = Depends(get_job_service)):
    pair = await compare_service.get_comparison(pair_id)
    if not pair:
        raise HTTPException(status_code=404, detail="Pasangan tidak ditemukan")

    # Jika HTMX request, kembalikan modal partial
    if request.headers.get("HX-Request"):
        # Pastikan relasi sudah di-fetch
        _ = pair.document_1
        _ = pair.document_2
        return templates.TemplateResponse(
            "partials/pair_detail_modal.html",
            {"request": request, "pair": pair, "threshold": threshold},
        )

    return JSONResponse({
        "id":     pair.id,
        "document_1": pair.document_1,
        "document_2": pair.document_2,
        "text_score":    pair.text_score,
        "code_score":    pair.code_score,
        "phrase_score":  pair.phrase_score,
        "final_score":   pair.final_score,
        "is_plagiat":    pair.is_plagiat,
        # "status": pair.status.value,
        # "note":   pair.note,
        # "action": pair.action,
    })


@router.get("/preview/{comparison_id}", name="document_preview")
async def preview_plagiarism(request: Request, comparison_id: UUID, compare_service = Depends(get_compare_service), service=Depends(get_convert_service)):
    comparison = await compare_service.get_comparison(comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Pasangan tidak ditemukan")

    pdf1, pdf2 = await service.convert_html(comparison_id)
    
    return templates.TemplateResponse(
        "pages/preview.html", 
        {
            "request": request, 
            "comparison": comparison,
            "dokumen_asli": pdf1, 
            "dokumen_sumber": pdf2
        }
    )

