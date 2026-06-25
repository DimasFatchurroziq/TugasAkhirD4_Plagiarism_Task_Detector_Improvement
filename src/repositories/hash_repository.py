import uuid
from typing import Dict, Any
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model import Hash


class HashRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_hash(self, document_id: str, hash: dict, type: str):
        hash = Hash(
            content=hash["hash_list"],
            fingerprint=hash["fingerprint_list"],
            type=type,
            document_id=document_id
        )
        self.db.add(hash)
        await self.db.commit()
        return hash

    async def get_by_doc(self, doc_id: str):
        result = await self.db.execute(
            select(Hash).where(
                Hash.document_id == doc_id
            )
        )
        return result.scalars().all()