from utils.similarity import jaccard_similarity
from utils.similarity import containment_similarity
# from utils.gst import greedy_string_tiling

class SimilarityService:
    def __init__(self, similarity_repository):
        self.similarity_repository = similarity_repository

    def similarity(self, tiles_list, length_1, length_2):
        intersection = 0
        min_length = min(length_1, length_2)

        for tile in tiles_list:
            # print(intersection)
            intersection += tile[2]
            
        
        similarity_1 = jaccard_similarity(intersection, length_1, length_2)  
        similarity_2 = containment_similarity(intersection, min_length)
        # print(sort_matched_list)
        # tiles_list = greedy_string_tiling(sort_matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len=3)

        return similarity_1, similarity_2
