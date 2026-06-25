class SBertService:

    def create_embedding_bulk(self, sentences: str):

        return self.model.encode(
            sentences,
            convert_to_tensor=True,
            normalize_embeddings=True
        )
        
