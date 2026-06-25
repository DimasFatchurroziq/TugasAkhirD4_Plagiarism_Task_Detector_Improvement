from fastapi import APIRouter, UploadFile, File, Depends
from src.api.v1.dependencies import get_job_service
from src.api.v1.dependencies import get_process_service, get_convert_service
from src.infrastructures.extraction.ocr import ocr_code_image
from pydantic import BaseModel
from typing import List
from uuid import UUID

from src.api.v1.schemas.job_schema import JobCreate, JobUpdate

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

# templates = Jinja2Templates(directory="src/templates")

process_router = APIRouter()


##############################################3


@process_router.post("/processmultiple/job/{job_id}", name="jobs_proses")
async def process_job_multiple(job_id: str, service=Depends(get_process_service)):
    return await service.process_job_multiple(job_id)

@process_router.post("/processsingle/job/{job_id}", name="jobs_proses")
async def process_job_single(job_id: str, service=Depends(get_process_service)):
    return await service.process_job_single(job_id)
 

#################################################333

@process_router.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    contents = await file.read()
    text = ocr_code_image(contents)

    return {"text": text}


@process_router.get("/blocks/{doc_id}")
async def get_bb(doc_id: str, service = Depends(get_job_service)):
    return await service.get_by_doc_id(doc_id)


# Model input untuk API
class CompareDocumentsRequest(BaseModel):
    docA: List[str]
    docB: List[str]

# Endpoint untuk melakukan perbandingan dokumen
@process_router.post("/compare")
async def compare_documents(request: CompareDocumentsRequest, service = Depends(get_job_service)):
    docA = request.docA
    docB = request.docB
    
    # Menggunakan service untuk memproses perbandingan
    results = service.compare_documents(docA, docB)
    
    return {"results": results}