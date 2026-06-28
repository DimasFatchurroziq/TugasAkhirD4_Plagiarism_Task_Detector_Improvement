# repositories/job_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from src.models.model import Job, Document
from uuid import UUID

from src.api.v1.schemas.job_schema import JobCreate, JobUpdate


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: JobCreate):
        job = Job(
            name = payload.name,
            description = payload.description,
            scenario = payload.scenario,
            threshold = payload.threshold,
            weight_text = payload.weight_text,
            weight_code = payload.weight_code,
            weight_phrase = payload.weight_phrase,
            )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        stmt = select(Job).options(selectinload(Job.documents)).where(Job.id == job.id)
        result = await self.db.execute(stmt)
        job_with_docs = result.scalars().first()
        return job_with_docs

    async def get_all(self):
        result = await self.db.execute(
            select(Job)
        )
        return result.scalars().all() 

    async def get_jobs_with_count(self):
        stmt = (
            select(Job)
            .options(selectinload(Job.documents))  # 🔥 eager load
            .order_by(Job.created_at.desc())
        )
        result = await self.db.execute(stmt)
        jobs = result.scalars().all()  # 🟢 scalars() penting!
        return jobs

    async def get_latest_jobs(self):
        stmt = (
            select(Job)
            .options(selectinload(Job.documents))  # 🔥 eager load
            .order_by(Job.created_at.desc())
            .limit(3)
        )
        result = await self.db.execute(stmt)
        jobs = result.scalars().all()  # 🟢 scalars() penting!
        return jobs

    async def get(self, job_id: UUID):
        result = await self.db.execute(
            select(Job)
            .options(selectinload(Job.documents))
            .where(Job.id == job_id)
        )
        return result.scalar_one_or_none()

    async def update(self, job, payload: JobUpdate):
        
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(job, key, value)
        
        await self.db.commit()
        await self.db.refresh(job)
        return job
    
    async def delete(self, job):
        await self.db.delete(job)
        await self.db.commit()
        return "job"


########################################################################################333
############################################################################################

    async def total_summary(self):

        stmt = select(
            func.count(Job.id).label("total"),

            func.sum(
                case(
                    (
                        Job.status == "ERROR",
                        1
                    ),
                    else_=0
                )
            ).label("error"),

            func.sum(
                case(
                    (
                        Job.status == "RUNNING",
                        1
                    ),
                    else_=0
                )
            ).label("running"),

            func.sum(
                case(
                    (
                        Job.status == "COMPLETED",
                        1
                    ),
                    else_=0
                )
            ).label("completed"),
        )

        result = await self.db.execute(stmt)

        return result.mappings().first()