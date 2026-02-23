from infrastructures.similarity.similarity import jaccard_similarity, containment_similarity
from infrastructures.rkr_gst.remove_contained import remove_contained

class SimilarityService:
    def __init__(self, similarity_repository):
        self.similarity_repository = similarity_repository

    def similarity(self, tiles_list, length_1, length_2):
        intersection = 0
        min_length = min(length_1, length_2)

        intervals = remove_contained(tiles_list)

        for interval in intervals:            
            intersection += interval
            
        similarity_1 = jaccard_similarity(intersection, length_1, length_2)  
        similarity_2 = containment_similarity(intersection, min_length)
        # print(sort_matched_list)
        # tiles_list = greedy_string_tiling(sort_matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len=3)

        return similarity_1, similarity_2
