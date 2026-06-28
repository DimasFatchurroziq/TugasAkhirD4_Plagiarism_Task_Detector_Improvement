from uuid import UUID
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model import Block, Mapping


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


    async def create_blocks_with_mappings(self, document_id: str, final_data: list[dict]):
        blocks_to_insert = []
        
        for item in final_data:
            # 1. Inisialisasi data block
            block_data = item["block"]
            block = Block(
                sequence=block_data["sequence"],
                content=block_data["content"],
                type=block_data["type"],
                source=block_data["source"],
                document_id=document_id
            )
            
            # 2. Inisialisasi data mapping
            map_data = item["mapping"]
            mapping = Mapping(
                mapping_doc=map_data["mapping_doc"],
                mapping_text_code=map_data["mapping_text_code"],
                mapping_preprocess=map_data["mapping_preprocess"],
                mapping_hash=map_data["mapping_hash"]
                # block_id TIDAK perlu diisi manual, karena diikat di bawah ini:
            )
            
            # 3. Hubungkan secara ORM (uselist=False)
            block.mapping = mapping
            
            blocks_to_insert.append(block)
            
        # 4. Kirim semuanya sekaligus ke database
        self.db.add_all(blocks_to_insert)
        await self.db.commit()  # Cukup sekali commit di akhir loop
        
        return blocks_to_insert