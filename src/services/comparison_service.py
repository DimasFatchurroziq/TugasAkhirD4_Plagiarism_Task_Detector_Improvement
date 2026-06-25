# services/job_service.py
from fastapi import HTTPException

import os
from uuid import UUID, uuid4
from pathlib import Path
import aiofiles

from src.models.model import Document

from typing import Optional

from src.api.v1.schemas.comparison_schema import ComparisonCreate, ComparisonUpdate


from src.services.job_service import JobService 
from src.services.document_service import DocumentService

from src.repositories.document_repository import DocumentRepository

from src.api.v1.schemas.document_schema import DocumentUpdate

class ComparisonService:
    def __init__(self, job_serv: JobService, doc_serv: DocumentService, compare_repo: DocumentRepository):
        self.job_serv = job_serv
        self.doc_serv = doc_serv

        self.compare_repo = compare_repo

    # async def create_job_documents(self, job_id: UUID, files, create_dir: str):
    #     job = await self.job_serv.get_job(job_id)

    #     if not job:
    #         raise ValueError("Job not found")

    #     folder = Path(create_dir) / str(job_id)
    #     folder.mkdir(parents=True, exist_ok=True)

    #     docs = []

    #     for file in files:
    #         filename = file.filename or "unknown"

    #         ext = filename.split(".")[-1] if "." in filename else "bin"
    #         safe_name = f"{uuid4()}.{ext}"

    #         path = folder / safe_name

    #         content = await file.read()

    #         # async file write (non-blocking)
    #         async with aiofiles.open(path, "wb") as f:
    #             await f.write(content)

    #         docs.append(Document(
    #             job_id=job_id,
    #             name=filename,
    #             path=str(path)
    #         ))

    #     result = await self.doc_repo.bulk_create(docs)

    #     return {
    #         "created": len(docs),
    #         "documents": result
    #     }

    
    async def get_all_job_comparisons(self, job_id: UUID):
        await self.job_serv.get_job(job_id)

        all_compare = await self.compare_repo.get_all_by_job(job_id)

        if all_compare is None:
            raise HTTPException(
                status_code=404,
                detail="All doc not found"
            )

        return all_compare

    async def get_all_doc_comparisons(self, document_id: UUID):
        await self.doc_serv.get_document(document_id)

        all_compare = await self.compare_repo.get_all_by_doc(document_id)

        if all_compare is None:
            raise HTTPException(
                status_code=404,
                detail="All doc not found"
            )

        return all_compare

    async def get_by_doc1_doc2(self, document_1_id : UUID, document_2_id : UUID):
        await self.doc_serv.get_document(document_1_id)
        await self.doc_serv.get_document(document_2_id)

        compare = await self.compare_repo.get_by_doc1_doc2(document_1_id, document_2_id)

        return compare

    async def get_comparison(self, compare_id: UUID):

        compare = await self.compare_repo.get(compare_id)

        if compare is None:
            raise HTTPException(
                status_code=404,
                detail="Doc not found"
            )

        return compare

    async def update_comparison(self, comparison_id: UUID, payload: ComparisonUpdate):
        compare = await self.get_comparison(comparison_id)

        return await self.compare_repo.update(compare, payload)

    # async def delete_job_document(self, job_id: UUID, document_id: UUID):
    #     doc = await self.get_job_document(job_id, document_id)

    #     return await self.doc_repo.delete(doc)


    
    
    
# ################################################################################################################################################################3
    
# from app.models.job import Job, FilePair, JobStatus, SimilarityLevel


# ── Stats ─────────────────────────────────────────────────────────


    # ── Pairs ─────────────────────────────────────────────────────────

    async def get_filter_comparison(self, filter_level: Optional[str] = None):
        if filter_level and filter_level != "all":
            return await self.compare_repo.get_filter_comparison(filter_level)
        return await self.compare_repo.get_filter_comparison(filter_level)


    async def get_pair(self, compare_id: UUID):
        return await self.compare_repo.get(compare_id)

    async def get_dashboard_summary(self):
        return await self.compare_repo.get_dashboard_summary()

    async def get_pairs(
        self,
        job_id: UUID,
        filter_level: str = "all"
    ):
        job = await self.job_serv.get_job(job_id)

        comparisons = await self.compare_repo.get_pairs(
            job_id=job_id,
            threshold = job.threshold / 100,
            filter_level=filter_level
        )

        return comparisons

    async def get_stats(self) -> dict:
        jobs = await self.job_serv.get_total_jobs()
        documents = await self.doc_serv.get_total_documents()
        comparisons = await self.get_dashboard_summary()
        return {
            "total_jobs":  jobs["total"],
            "total_documents": documents["total"],
            "total_files": comparisons["total"],
            "high_sim":    comparisons["high"],
            "med_sim":     comparisons["med"],
        }


    
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


    async def process_document(self, document_id: str):
        doc = await self.doc_repo.get(document_id)

        if not doc:
            raise Exception("Document not found")

        if doc.status != "UPLOADED":
            return {"message": "Already processed or in progress"}

        doc.status = "PROCESSING"
        await self.doc_repo.save(doc)

        # trigger async worker
        self.enqueue_document(doc.id)

        return {
            "message": "Processing started",
            "document_id": str(doc.id)
        }