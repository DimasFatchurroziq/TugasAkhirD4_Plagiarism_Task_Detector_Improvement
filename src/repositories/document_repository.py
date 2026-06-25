# repositories/document_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from src.models.model import Document, Comparison
from sqlalchemy.orm import aliased, joinedload

from uuid import UUID

from src.api.v1.schemas.document_schema import DocumentUpdate

class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def bulk_create(self, docs: list[Document]):
        self.db.add_all(docs)
        # print("BEFORE COMMIT")
        await self.db.commit()
        # print("AFTER COMMIT")
        for doc in docs:
            await self.db.refresh(doc)

        return docs

    async def get_all_by_job(self, job_id: UUID):
        result = await self.db.execute(
            select(Document).where(Document.job_id == job_id)
        )
        return result.scalars().all()

    async def get_all_by_job_category(self, job_id: UUID, category: str):
        result = await self.db.execute(
            select(Document).where(
                Document.job_id == job_id,
                Document.category == category
                )
        )
        return result.scalars().all()

    async def get(self, document_id: UUID):
        result = await self.db.execute(
            select(Document).filter(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def update(self, doc, payload: DocumentUpdate):
        
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(doc, key, value)

        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def delete(self, doc):
        await self.db.delete(doc)
        await self.db.commit()
        return "doc"


########################################################################################333
############################################################################################


    async def get_documents_by_comparison_id(
        self,
        comparison_id
    ):
        result = await self.db.execute(
            select(Comparison)
            .options(
                joinedload(Comparison.document_1),
                joinedload(Comparison.document_2)
            )
            .where(Comparison.id == comparison_id)
        )

        comparison = result.scalar_one_or_none()

        if not comparison:
            return None

        return {
            "document_1": comparison.document_1,
            "document_2": comparison.document_2
        }

    async def total_summary(self):

        stmt = select(
            func.count(Document.id).label("total"),

            func.sum(
                case(
                    (
                        Document.status == "UPLOADED",
                        1
                    ),
                    else_=0
                )
            ).label("uploaded"),

            func.sum(
                case(
                    (
                        Document.status == "PROCESSING",
                        1
                    ),
                    else_=0
                )
            ).label("processing"),

            func.sum(
                case(
                    (
                        Document.status == "DONE",
                        1
                    ),
                    else_=0
                )
            ).label("done"),

            func.sum(
                case(
                    (
                        Document.status == "ERROR",
                        1
                    ),
                    else_=0
                )
            ).label("error"),
        )

        result = await self.db.execute(stmt)

        return result.mappings().first()


    async def get_pairs(
        self,
        job_id: UUID,
        filter_level: str = "total"
    ):

        stmt = (
            select(
                func.count(Document.id).label("total"),

                func.sum(
                    case(
                        (Document.status == "UPLOADED", 1),
                        else_=0
                    )
                ).label("uploaded"),

                func.sum(
                    case(
                        (Document.status == "PROCESSING", 1),
                        else_=0
                    )
                ).label("processing"),

                func.sum(
                    case(
                        (Document.status == "DONE", 1),
                        else_=0
                    )
                ).label("done"),

                func.sum(
                    case(
                        (Document.status == "ERROR", 1),
                        else_=0
                    )
                ).label("error"),
            )
            .where(Document.job_id == job_id)
        )

        result = await self.db.execute(stmt)

        return result.mappings().first()


    async def get_pairsss(
        self,
        job_id: UUID,
        filter_level: str = "total"
    ):


        stmt = (
            select(Document).where(Document.job_id == job_id)
        )

        # FILTER LEVEL

        if filter_level == "uploaded":
            stmt = stmt.where(
                Document.status == "UPLOADED"
            )

        elif filter_level == "processing":
            stmt = stmt.where(
                Document.status == "PROCESSING"
            )

        elif filter_level == "done":
            stmt = stmt.where(
                Document.status == "DONE"
            )

        elif filter_level == "error":
            stmt = stmt.where(
                Document.status == "ERROR"
            )

        # print(filter_level)

        stmt = stmt.distinct()

        result = await self.db.execute(stmt)

        return result.scalars().all()













    async def update_status(self, document_id: UUID, status: UUID):
        doc = await self.db.get(Document, document_id)

        if not doc:
            raise Exception("Document not found")

        doc.status = status

        await self.db.commit()
        await self.db.refresh(doc)

        return doc
