# @@@@ tahap 4
# sorting
# searching
# gst
# (tile)

# asal dari rkr service
from src.utils.sorting import timsort
from src.infrastructures.rkr_gst.searching import binary_search

# asala  dari gst service
from src.utils.sorting import timsort
from src.infrastructures.rkr_gst.gst import gst_right_left

class Tahap_4:
    # def __init__(self, tahap_4_repository):
    #     self.tahap_4_repository = tahap_4_repository

    def rkr(self, fingerprint_list_1, fingerprint_list_2, rollinghash_list_1, rollinghash_list_2, min_match_len):
        # get fingerprint_list_1, fingerprint_list_2, rollinghash_list_1, rollinghash_list_2 dari database
        
        sort_fingerprint_2 = timsort(fingerprint_list_2, 1)
        
        result = []
        for item in fingerprint_list_1:
            sort_matched_list = binary_search(sort_fingerprint_2, item, 1)
            result.extend(sort_matched_list)

        # print(result)

        double_tiles, length_1, length_2 = gst_right_left(result, rollinghash_list_1, rollinghash_list_2, min_match_len)

        # print(double_tiles)

        # await self.tahap_3_repository.save_fingerprints(document_id, fingerprint_list) ganti menjadi upload tile list

        return double_tiles, length_1, length_2













# class GstService:
#     def __init__(self, gst_repository):
#         self.gst_repository = gst_repository

#     def gst(self, sort_matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len):

#         tiles_list, length_1, length_2 = gst_right_left(sort_matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len)

#         # print(tiles_list)

#         return tiles_list, length_1, length_2