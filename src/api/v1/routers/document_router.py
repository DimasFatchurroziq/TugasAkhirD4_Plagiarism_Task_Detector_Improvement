# api/routes.py
from fastapi import APIRouter, UploadFile, File, Depends
from src.api.v1.dependencies import get_doc_service

from src.api.v1.schemas.document_schema import DocumentUpdate

from uuid import UUID

document_router = APIRouter()

UPLOAD_DIR = "uploads"

@document_router.post("/jobs/{job_id}/documents")
async def create_job_documents(
    job_id: UUID,
    files: list[UploadFile] = File(...),
    service = Depends(get_doc_service)
    ):
    return await service.create_job_documents(job_id, files, UPLOAD_DIR)

@document_router.get("/jobs/{job_id}/documents")
async def get_all_job_documents(
    job_id: UUID,
    service = Depends(get_doc_service)
    ):
    return await service.get_all_job_documents(job_id)

@document_router.get("/documents/{document_id}")
async def get_document(
    document_id: UUID,
    service = Depends(get_doc_service)
    ):
    return await service.get_document(document_id)

@document_router.put("/documents/{document_id}")
async def update_job_document(
    document_id: UUID,
    payload: DocumentUpdate,
    service = Depends(get_doc_service)
    ):
    return await service.update_document(document_id, payload)

@document_router.delete("/documents/{document_id}")
async def delete_job_document(
    document_id: UUID,
    service = Depends(get_doc_service)
    ):
    return await service.delete_document(document_id)