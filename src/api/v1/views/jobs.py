from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from src.api.v1.schemas.job_schema import JobCreate, JobUpdate
from src.api.v1.dependencies import get_job_service, get_compare_service
from src.services import dashboard_service, job_service
from src.core.templates import templates
from uuid import UUID

router    = APIRouter(prefix="/jobs")

@router.get("/", name="jobs_list")
async def jobs_list(request: Request, compare_service = Depends(get_compare_service), service = Depends(get_job_service)):
    count_jobs = await service.get_total_jobs()

    jobs  = await service.get_all_jobs_with_count()
    stats = await compare_service.get_stats()
    return templates.TemplateResponse(
        "pages/jobs.html",
        {
            "request":     request,
            "active_page": "jobs",
            "page_title":  "Daftar Job",
            "jobs":        jobs,
            "counts":      count_jobs,
            "stats":       stats,
        },
    )


@router.post("/create", name="jobs_create")
async def jobs_create(
    request:   Request,
    name:      str = Form(...),
    description:str = Form(default=""),
    scenario:  str = Form(default="MULTIPLE"),
    threshold: int = Form(default=70),
    weight_text: int = Form(default=10),
    weight_code: int = Form(default=85),
    weight_phrase: int = Form(default=5),
    job_service = Depends(get_job_service),
    # payload: JobCreate
):
    payload = JobCreate(
        name=name, 
        description=description, 
        scenario=scenario, 
        threshold=threshold,
        weight_text=weight_text/100,
        weight_code=weight_code/100,
        weight_phrase=weight_phrase/100,
    )

    job    = await job_service.create_job(payload)

    if request.headers.get("HX-Request"):
        response = templates.TemplateResponse(
            "partials/job_card.html",
            {"request": request, "job": job},
        )

        target_url = f"{request.url_for('upload_page')}?job_id={job.id}"
    
        response.headers["HX-Trigger"] = f'{{"jobCreatedDelayed": "{target_url}"}}'
        return response

    return RedirectResponse(url="/jobs/", status_code=303)


@router.post("/{job_id}/update", name="jobs_update")
async def jobs_update(
    request:   Request,
    job_id: UUID,
    name:      str = Form(...),
    description:str = Form(default=""),
    threshold: int = Form(default=70),
    weight_text: int = Form(default=10),
    weight_code: int = Form(default=85),
    weight_phrase: int = Form(default=5),
    job_service = Depends(get_job_service),
):
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job tidak ditemukan")

    payload = JobUpdate(
        name=name, 
        description=description, 
        threshold=threshold,
        weight_text=weight_text/100,
        weight_code=weight_code/100,
        weight_phrase=weight_phrase/100,
    )

    job    = await job_service.update_job_with_status(job.id, payload)

    if request.headers.get("HX-Request"):
        print(job)
        return templates.TemplateResponse(
            "partials/job_card.html",
            {"request": request, "job": job},
        )


    return RedirectResponse(url="/jobs/", status_code=303)

@router.delete("/{job_id}", name="jobs_delete")
async def jobs_delete(job_id: UUID, job_service = Depends(get_job_service)):
    try:
        # Sesuaikan dengan string path tempat kamu menyimpan upload file, misalnya "uploads" atau "storage"
        base_dir = "uploads" 
        
        await job_service.delete_job(job_id, base_dir=base_dir)
        return JSONResponse(content={"ok": True, "message": "Job and its folder deleted successfully"}, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}", name="jobs_detail")
async def jobs_detail(request: Request, job_id: UUID, compare_service = Depends(get_compare_service), job_service = Depends(get_job_service)):
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job tidak ditemukan")

    all_pairs = await compare_service.get_pairs(
        job_id=job_id,
        filter_level="all"
    )

    total = [
        p.id or 0
        for p in all_pairs
    ]

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "partials/job_detail_modal.html",
            {"request": request, "job": job, "pairs": len(total)},
        )

    return JSONResponse({
        "id":     job.id,
        "name": job.name,
        "created_at": job.created_at,
        "description":    job.description,
        "scenario":    job.scenario,
        "threshold":  job.threshold,
        "status":    job.status,
        "progress": job.progress,
        "weight_text": job.weight_text,
        "weight_code": job.weight_code,
        "weight_phrase": job.weight_phrase,
    })


@router.get("/{job_id}/edit", name="jobs_edit")
async def jobs_edit(
    request: Request, 
    job_id: UUID, 
    job_service = Depends(get_job_service)
):
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job tidak ditemukan")

    if request.headers.get("HX-Request"):
        print(1)
        return templates.TemplateResponse(
            "partials/edit_job_modal.html",  # <-- Ini file baru yang akan kita buat
            {"request": request, "job": job},
        )
    print(2)
    # Backup jika diakses langsung lewat URL browser (bukan HTMX)
    return JSONResponse({"status": "Hanya menerima request via HTMX"})