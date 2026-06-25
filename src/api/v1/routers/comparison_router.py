# api/routes.py
from fastapi import APIRouter, UploadFile, File, Depends
from src.api.v1.dependencies import get_compare_service

from src.api.v1.schemas.comparison_schema import ComparisonCreate, ComparisonUpdate

from uuid import UUID

comparison_router = APIRouter()

UPLOAD_DIR = "uploads"

# @comparison_router.post("/comparisons")
# async def create_job_documents(
#     job_id: UUID,
#     files: list[UploadFile] = File(...),
#     service = Depends(get_doc_service)
#     ):
#     return await service.create_job_documents(job_id, files, UPLOAD_DIR)

@comparison_router.get("/jobs/{job_id}/comparisons")
async def get_all_job_comparisons(
    job_id: UUID,
    service = Depends(get_compare_service)
    ):
    return await service.get_all_job_comparisons(job_id)

@comparison_router.get("/documents/{document_id}/comparisons")
async def get_all_doc_comparisons(
    document_id: UUID,
    service = Depends(get_compare_service)
    ):
    return await service.get_all_doc_comparisons(document_id)

@comparison_router.get("/comparisons/{comparison_id}")
async def get_job_comparison(
    comparison_id: UUID,
    service = Depends(get_compare_service)
    ):
    return await service.get_comparison(comparison_id)

@comparison_router.put("/comparisons/{comparison_id}")
async def update_job_document(
    comparison_id: UUID,
    payload: ComparisonUpdate,
    service = Depends(get_compare_service)
    ):
    return await service.update_comparison(comparison_id, payload)

# @comparison_router.delete("/comparisons/{comparison_id}")
# async def delete_job_document(
#     job_id: UUID,
#     comparison_id: UUID,
#     service = Depends(get_doc_service)
#     ):
#     return await service.delete_job_document(job_id, comparison_id)