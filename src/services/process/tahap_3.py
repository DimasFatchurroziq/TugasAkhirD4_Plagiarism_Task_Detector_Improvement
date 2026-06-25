# @@@@ tahap 3
# ngrams_generate
# rollinghash_generate
# index_generate
# ngrams_generate as window_generate
# fingerprint_generate
# (fingerprint, rolling hash)


# asal dari rolling hash service
from src.infrastructures.rollinghash.ngrams_generate import generate_ngrams
from src.infrastructures.rollinghash.rollinghash_generate import rollinghash_text

# asal dari winnowing sevice
from src.utils.index_generate import generate_index
from src.infrastructures.rollinghash.ngrams_generate import generate_ngrams
from src.infrastructures.winnowing.fingerprint_generate import fingerprint_generate

class Tahap_3:
    # def __init__(self, tahap_3_repository):
    #     self.tahap_3_repository = tahap_3_repository

    async def rollinghash(self, tokens_list, n_gram, n_window):

        final_hash = []
        # asal dari rolling hash service
        ngrams_list = generate_ngrams(tokens_list, n_gram)
        hash_list = rollinghash_text(ngrams_list)
        
        # asal dari winnowing sevice
        indexing_list = generate_index(hash_list)

        window_list = generate_ngrams(indexing_list, n_window)
        fingerprint_list = fingerprint_generate(window_list)

        # await self.tahap_3_repository.save_fingerprints(document_id, fingerprint_list) 

        final_hash = {
            "hash_list": hash_list, 
            "fingerprint_list": fingerprint_list
        }

        return final_hash
















# class WinnowingService:
#     # def __init__(self, repository_winnowing):
#     #     self.repository_winnowing = repository_winnowing

#     def winnowing(self, hash_list, n):
#         indexing_list = generate_index(hash_list)

#         window_list = generate_ngrams(indexing_list, n=7)
#         fingerprint_list = fingerprint_generate(window_list)

#         # print(window_list)

#         return fingerprint_list