# services/job_service.py
from fastapi import HTTPException
from pathlib import Path
import shutil
from fastapi import HTTPException

import os
from uuid import UUID

from src.api.v1.schemas.job_schema import JobCreate, JobUpdate


class JobService:
    def __init__(self, job_repo):
        self.job_repo = job_repo

    async def create_job(self, payload: JobCreate):
        return await self.job_repo.create(payload)

    async def get_all_jobs(self):
        return await self.job_repo.get_all()
    
    async def get_all_jobs_with_count(self):
        return await self.job_repo.get_jobs_with_count()

    async def get_latest_jobs(self):
        return await self.job_repo.get_latest_jobs()

    async def get_job(self, job_id: UUID):
        job = await self.job_repo.get(job_id)
        if job is None:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        return job

    async def update_job(self, job_id: UUID, payload: JobUpdate):
        job = await self.get_job(job_id)
        return await self.job_repo.update(job, payload)

    async def update_job_with_status(self, job_id: UUID, payload: JobUpdate):
        job = await self.get_job(job_id)
        updated_payload = payload.model_copy(update={"status": "MODIFIED"})
        return await self.job_repo.update(job, updated_payload)

    async def delete_job(self, job_id: UUID, base_dir: str):
        # 1. Pastikan Job-nya ada di DB
        job = await self.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job tidak ditemukan")

        # 2. Hapus folder lokal milik Job (entah kosong atau ada isinya)
        # Folder didefinisikan berdasarkan base_dir / job_id seperti saat create
        job_folder = Path(base_dir) / str(job_id)
        
        try:
            if job_folder.exists() and job_folder.is_dir():
                # shutil.rmtree akan menghapus folder beserta SELURUH file di dalamnya secara instan
                shutil.rmtree(job_folder)
                print(f"Folder job {job_id} berhasil dihapus dari lokal.")
            else:
                print(f"Peringatan: Folder lokal {job_folder} tidak ditemukan, lanjut hapus DB.")
        except Exception as e:
            # Kita log error-nya agar jika gagal karena permission issue, kita tahu.
            print(f"Gagal menghapus folder lokal {job_folder}. Error: {e}")

        # 3. Hapus data Job dari database via Repository
        return await self.job_repo.delete(job)


##############################################################################################3
##############################################################################################3

    async def get_total_jobs(self):
        return await self.job_repo.total_summary()

    