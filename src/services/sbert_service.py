from src.repositories.block_embedding_repository import BlockEmbeddingRepository
from src.models.model import BlockEmbedding

class SBertService:
    def __init__(self, block_embed_repo: BlockEmbeddingRepository):
        self.block_embed_repo = block_embed_repo

    def create_embedding_bulk(self, sentences: str):
        block_embed_objects = []

        for item in block_embed_list:
            obj = BlockEmbedding(
                embedding=item
            )
            block_embed_objects(obj)

        return self.model.encode(
            sentences,
            convert_to_tensor=True,
            normalize_embeddings=True
        )
        
