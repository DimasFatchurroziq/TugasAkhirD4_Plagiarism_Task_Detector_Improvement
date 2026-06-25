from uuid import UUID
from typing import Dict, Any
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model import Rkrgst


class RkrgstRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_rkrgst(self, comparison_id: str, rkrgst: list, type: str):
        rkrgst = Rkrgst(
            type=type,
            position_1_start=rkrgst[0],
            position_2_start=rkrgst[1],
            match_length=rkrgst[2],
            comparison_id=comparison_id
        )
        self.db.add(rkrgst)
        await self.db.commit()
        return rkrgst

    async def bulk_create(self, rkrgst_objects: list[Rkrgst]):
        
        self.db.add_all(rkrgst_objects)
        
        await self.db.commit()
        
        return rkrgst_objects

    async def get_by_compare(self, compare_id: UUID):
        result = await self.db.execute(
            select(Rkrgst).where(
                Rkrgst.comparison_id == compare_id,
            )
        )
        return result.scalars().all()        
