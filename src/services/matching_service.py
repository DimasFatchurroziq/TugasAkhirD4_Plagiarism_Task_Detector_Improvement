from utils.sorting import timsort
from utils.searching import binary_search

class MatchingService:
    # def __init__(self, repository_rollinghash):
    #     self.repository_rollinghash = repository_rollinghash

    def matching(self, fingerprint_list_1, fingerprint_list_2):
        sort_fingerprint_2 = timsort(fingerprint_list_2, 1)
        
        result = []
        for item in fingerprint_list_1:
            sort_matched_list = binary_search(sort_fingerprint_2, item, 1)
            result.extend(sort_matched_list)

        return result
