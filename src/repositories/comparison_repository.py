# repositories/job_repo.py
from uuid import UUID

from typing import Dict, Any

from sqlalchemy.orm import aliased, joinedload, selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func, case, desc
from src.models.model import Comparison, Job, Document

from src.api.v1.schemas.comparison_schema import ComparisonCreate, ComparisonUpdate

class ComparisonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_compare(self, document_1_id: str, document_2_id: str):
        comparison = Comparison(
            document_1_id=document_1_id,
            document_2_id=document_2_id
        )
        self.db.add(comparison)
        await self.db.commit()
        await self.db.refresh(comparison)
        return comparison

    async def update(self, comparison, payload: ComparisonUpdate):
        
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(comparison, key, value)

        await self.db.commit()
        await self.db.refresh(comparison)
        return comparison

    async def get_all_by_job(self, job_id: UUID):
        Doc1 = aliased(Document)
        Doc2 = aliased(Document)

        stmt = (
            select(Comparison)
            .join(Doc1, Comparison.document_1)
            .join(Doc2, Comparison.document_2)
            .where(
                or_(
                    Doc1.job_id == job_id,
                    Doc2.job_id == job_id
                )
            )
            .distinct()
        )

        result = await self.db.execute(stmt)
        comparisons = result.scalars().all()
        return comparisons

    async def get_all_by_doc(self, document_id: UUID):
        stmt = (
            select(Comparison)
            .where(
                or_(
                    Comparison.document_1_id == document_id,
                    Comparison.document_2_id == document_id
                )
            )
        )

        result = await self.db.execute(stmt)
        comparisons = result.scalars().all()
        return comparisons

    async def get_by_doc1_doc2(self, document_1_id : UUID, document_2_id : UUID):
        stmt = select(Comparison).where(
            or_(
                and_(
                    Comparison.document_1_id == document_1_id,
                    Comparison.document_2_id == document_2_id,
                ),
                and_(
                    Comparison.document_1_id == document_2_id,
                    Comparison.document_2_id == document_1_id,
                ),
            )
        )

        result = await self.db.execute(stmt)
        comparisons = result.scalars().first()
        return comparisons

    async def get(self, compare_id: UUID):
        result = await self.db.execute(
            select(Comparison)
            .options(
                selectinload(Comparison.document_1),
                selectinload(Comparison.document_2)
            )
            .where(Comparison.id == compare_id)
        )
        return result.scalars().first()

    # repositories/document_repository.py
# #########################################################################################################################

    # async def get_filter_comparison(
    #     self,
    #     plagiarism_level: str = "all"
    # ):
    #     stmt = select(Comparison)

    #     if plagiarism_level == "low":
    #         stmt = stmt.where(
    #             Comparison.final_score <= 0.3
    #         )

    #     elif plagiarism_level == "med":
    #         stmt = stmt.where(
    #             Comparison.final_score.between(0.31, 0.7)
    #         )

    #     elif plagiarism_level == "high":
    #         stmt = stmt.where(
    #             Comparison.final_score > 0.7
    #         )

    #     result = await self.db.execute(stmt)

    #     return result.scalars().all()

    async def get_dashboard_summary(self):

        stmt = select(
            func.count(Comparison.id).label("total"),

            func.sum(
                case(
                    (
                        Comparison.final_score <= 0.4,
                        1
                    ),
                    else_=0
                )
            ).label("low"),

            func.sum(
                case(
                    (
                        Comparison.final_score.between(0.41, 0.7),
                        1
                    ),
                    else_=0
                )
            ).label("med"),

            func.sum(
                case(
                    (
                        Comparison.final_score > 0.7,
                        1
                    ),
                    else_=0
                )
            ).label("high"),
        )

        result = await self.db.execute(stmt)

        return result.mappings().first()


    async def get_pairs(
        self,
        job_id: UUID,
        threshold: int = 0.7,
        filter_level: str = "all"
    ):

        Doc1 = aliased(Document)
        Doc2 = aliased(Document)

        stmt = (
            select(Comparison)
            .options(
                joinedload(Comparison.document_1),
                joinedload(Comparison.document_2),
            )
            .join(Doc1, Comparison.document_1)
            .join(Doc2, Comparison.document_2)
            .where(
                or_(
                    Doc1.job_id == job_id,
                    Doc2.job_id == job_id
                )
            )
            .order_by(desc(Comparison.final_score))
        )

        # FILTER LEVEL

        if filter_level == "low":
            stmt = stmt.where(
                Comparison.final_score < 0.4
            )

        elif filter_level == "med":
            stmt = stmt.where(
                Comparison.final_score >= 0.4,
                Comparison.final_score < threshold
            )

        elif filter_level == "high":
            stmt = stmt.where(
                Comparison.final_score >= threshold
            )

        elif filter_level == "plag":
            stmt = stmt.where(
                Comparison.is_plagiat == True
            )

        # print(filter_level)

        stmt = stmt.distinct()

        result = await self.db.execute(stmt)

        return result.scalars().all()