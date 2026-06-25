# api/routes.py
from fastapi import APIRouter, UploadFile, File, Depends
from src.api.v1.dependencies import get_job_service
from src.infrastructures.extraction.ocr import ocr_code_image
from pydantic import BaseModel
from typing import List

from uuid import UUID

from src.api.v1.schemas.job_schema import JobCreate, JobUpdate

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

# templates = Jinja2Templates(directory="src/templates")

job_router = APIRouter()

@job_router.post("/jobs")
async def create_job(payload: JobCreate, service = Depends(get_job_service)):
    return await service.create_job(payload)

@job_router.get("/jobs")
async def get_all_jobs(service = Depends(get_job_service)):
    return await service.get_all_jobs()

@job_router.get("/jobss/{job_id}")
async def get_job(job_id: UUID, service = Depends(get_job_service)):
    return await service.get_job(job_id)

@job_router.put("/jobs_1/{job_id}")
async def update_job(job_id: UUID, payload: JobUpdate, service = Depends(get_job_service)):
    return await service.update_job(job_id, payload)

@job_router.delete("/jobs_1/{job_id}")
async def delete_job(job_id: UUID, service = Depends(get_job_service)):
    return await service.delete_job(job_id)


