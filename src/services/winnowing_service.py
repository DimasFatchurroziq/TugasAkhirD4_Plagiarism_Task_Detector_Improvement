from utils.index_generate import generate_index
from utils.ngrams_generate import generate_ngrams
from utils.fingerprint_generate import fingerprint_generate

class WinnowingService:
    # def __init__(self, repository_winnowing):
    #     self.repository_winnowing = repository_winnowing

    def winnowing(self, hash_list, n):
        indexing_list = generate_index(hash_list)

        window_list = generate_ngrams(indexing_list, n=4)
        fingerprint_list = fingerprint_generate(window_list)

        return fingerprint_list

