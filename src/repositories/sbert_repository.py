import uuid
from typing import Dict, Any
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model import SBert


class SBertRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_sbert(self, comparison_id: str, sbert: dict):
        sbert = SBert(
            block_1_id=sbert["block_1_id"],
            block_2_id=sbert["block_2_id"],
            score=sbert["score"],
            comparison_id=comparison_id
        )
        self.db.add(sbert)
        await self.db.commit()
        return sbert
