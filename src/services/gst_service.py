from utils.sorting import timsort
from utils.gst import greedy_string_tiling

class GstService:
    def __init__(self, gst_repository):
        self.gst_repository = gst_repository

    def gst(self, sort_matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len):

        tiles_list, length_1, length_2 = greedy_string_tiling(sort_matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len)

        return tiles_list, length_1, length_2
