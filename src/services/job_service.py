# services/job_service.py
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

    async def delete_job(self, job_id: UUID):
        job = await self.get_job(job_id)
        return await self.job_repo.delete(job)


##############################################################################################3
##############################################################################################3

    async def get_total_jobs(self):
        return await self.job_repo.total_summary()