from infrastructures.rollinghash.ngrams_generate import generate_ngrams
from infrastructures.rollinghash.rollinghash_generate import rollinghash_text

class RollingHashService:
    def __init__(self, hash_repository):
        self.hash_repository = hash_repository

    async def rollinghash_text(self, tokens_list, n=3):
        ngrams_list = generate_ngrams(tokens_list, n)
        hash_list = rollinghash_text(ngrams_list)

        # print(hash_list)

        # rollinghash_list = await self.repository_rollinghash.create(hash_list)

        return hash_list

    