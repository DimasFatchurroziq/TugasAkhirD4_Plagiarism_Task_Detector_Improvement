import uuid
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model import Mapping


class MappingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_mapping(self, block_id: str, mapping: dict):
        mapping = Mapping(
            mapping_doc=mapping["mapping_doc"],
            mapping_text_code=mapping["mapping_text_code"],
            mapping_preprocess=mapping["mapping_preprocess"],
            mapping_hash=mapping["mapping_hash"],
            block_id=block_id
        )
        self.db.add(mapping)
        await self.db.commit()
        return mapping

    async def update_is_detect(self, mapping_id: str, is_detect: bool):
        mapping = await self.db.get(Mapping, mapping_id)

        if not mapping:
            raise Exception("Mapping not found")

        mapping.is_detect = is_detect

        await self.db.commit()
        await self.db.refresh(mapping)

        return mapping

    async def get_by_doc(self, document_id: str):
        result = await self.db.execute(
            select(Mapping).where(Mapping.document_id == document_id)
        )
        return result.scalars().all()