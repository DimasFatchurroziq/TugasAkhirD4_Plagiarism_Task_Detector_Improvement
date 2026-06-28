# services/job_service.py
from fastapi import HTTPException
from pathlib import Path
import os
from uuid import UUID, uuid4
from pathlib import Path
import aiofiles

from src.models.model import Document

from src.services.job_service import JobService

from src.repositories.document_repository import DocumentRepository

from src.api.v1.schemas.document_schema import DocumentUpdate

class DocumentService:
    def __init__(self, job_serv: JobService, doc_repo: DocumentRepository):
        self.job_serv = job_serv

        self.doc_repo = doc_repo

    async def create_job_documents(self, job_id: UUID, files, category, create_dir: str):

        if not isinstance(files, list):
            files = [files] # <-- FIX UTAMA

        job = await self.job_serv.get_job(job_id)

        if not job:
            raise ValueError("Job not found")

        folder = Path(create_dir) / str(job_id)
        folder.mkdir(parents=True, exist_ok=True)

        docs = []
        # print(files)

        for file in files:
            # print(file)
            filename = file.filename or "unknown"

            ext = filename.split(".")[-1] if "." in filename else "bin"
            safe_name = f"{uuid4()}.{ext}"

            path = folder / safe_name

            content = await file.read()

            # async file write (non-blocking)
            async with aiofiles.open(path, "wb") as f:
                await f.write(content)

            docs.append(Document(
                job_id=job_id,
                name=filename,
                path=str(path),
                category=category
            ))

        result = await self.doc_repo.bulk_create(docs)

        return {
            "created": len(docs),
            "documents": result
        }

    
    async def get_all_job_documents(self, job_id: UUID):
        await self.job_serv.get_job(job_id)

        all_docs = await self.doc_repo.get_all_by_job(job_id)

        if all_docs is None:
            raise HTTPException(
                status_code=404,
                detail="All doc not found"
            )

        return all_docs

    async def get_document(self, document_id: UUID):
        doc = await self.doc_repo.get(document_id)
        if doc is None:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        return doc

    async def update_document(self, document_id: UUID, payload: DocumentUpdate):
        doc = await self.get_document(document_id)

        return await self.doc_repo.update(doc, payload)


    async def delete_document(self, document_id: UUID):
        # Ini akan otomatis raise HTTPException jika data tidak ada di DB
        doc = await self.get_document(document_id) 
        
        if hasattr(doc, 'path') and doc.path:
            file_path = Path(doc.path)
            try:
                # Menggunakan os.path.exists secara sinkronus atau pakai anyio
                if file_path.exists() and file_path.is_file():
                    # Pilihan 1: Menggunakan standard library (blocking sedikit tidak masalah untuk single file)
                    file_path.unlink()
                    
                    # Pilihan 2: Jika ingin benar-benar non-blocking (async), gunakan anyio:
                    # await anyio.to_thread.run_sync(file_path.unlink)
                    
                    print(f"Berhasil menghapus file fisik: {file_path}")
                else:
                    print(f"Peringatan: File fisik tidak ditemukan di {file_path}, lanjut hapus data DB.")
            except Exception as e:
                # Kita log error-nya, tapi proses di DB tetap lanjut agar tidak ada data 'sampah' di DB
                print(f"Gagal menghapus file fisik di {doc.path}. Error: {e}")

        # Hapus data di database
        await self.doc_repo.delete(doc)
        
        return {"message": "Document and physical file deleted successfully", "id": document_id}


##############################################################################################3
##############################################################################################3


    async def get_document_comparison(self, comparison_id: UUID):
        doc = await self.get_documents_by_comparison_id(comparison_id)

        return doc

    async def get_total_documents(self):
        return await self.doc_repo.total_summary()


    async def get_pairs(
        self,
        job_id: UUID,
        filter_level: str = "total"
    ):
        await self.job_serv.get_job(job_id)

        documents = await self.doc_repo.get_pairsss(
            job_id=job_id,
            filter_level=filter_level
        )

        return documents
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


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