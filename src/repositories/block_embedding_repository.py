import uuid
from typing import Dict, Any
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model import BlockEmbedding


class BlockEmbeddingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_block_embed(self, block_embed_data: dict):
        # 1. Cek langsung ke database apakah block_id ini sudah punya embedding
        stmt = select(BlockEmbedding).where(BlockEmbedding.block_id == block_embed_data["block_id"])
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        # 2. Jika database menjawab "Sudah ada", langsung skip (kembalikan data yang ada)
        if existing:
            return existing
            
        # 3. Jika belum ada di database, baru aman untuk di-INSERT
        new_block_embed = BlockEmbedding(
            block_id=block_embed_data["block_id"],
            embedding=block_embed_data["embedding"],
        )
        self.db.add(new_block_embed)
        await self.db.commit()
        return new_block_embed