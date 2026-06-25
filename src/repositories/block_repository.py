from uuid import UUID
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model import Block


class BlockRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_block(self, document_id: str, block: dict):
        block = Block(
            sequence=block["sequence"],
            content=block["content"],
            type=block["type"],
            source=block["source"],
            document_id=document_id
        )
        self.db.add(block)
        await self.db.flush()
        await self.db.refresh(block)
        return block

    async def get_by_doc_id(self, doc_id: str, type: str):
        result = await self.db.execute(
            select(Block).where(
                Block.document_id == doc_id,
                Block.type == type
            )
        )
        return result.scalars().all()

    async def get_by_doc_with_map_embed(self, doc_id: str, type: str):
        result = await self.db.execute(
            select(Block)
            .options(
                joinedload(Block.block_embedding),
                joinedload(Block.mapping)
            )
            .where(
                Block.document_id == doc_id,
                Block.type == type # Menggunakan nama variabel yang jelas, bukan 'type'
            )
            .order_by(Block.sequence)
        )
        return result.scalars().unique().all()

    async def get_by_doc_with_map(self, doc_id: UUID):
        result = await self.db.execute(
            select(Block)
            .options(
                joinedload(Block.mapping)
            )
            .where(
                Block.document_id == doc_id,
            )
            .order_by(Block.sequence)
        )
        return result.scalars().unique().all()