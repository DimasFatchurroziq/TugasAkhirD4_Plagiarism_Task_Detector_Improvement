from src.infrastructures.rkr_gst.gst import gst_tile_to_hash_map, gst_hash_to_textcode_map, gst_textcode_to_doc_map
from src.infrastructures.sentence_bert.sbert import embed_sentences
from src.infrastructures.preprocessing.text_tokenize import count_word


class Tahap_8:

    def reverse_map(self, blocks, double_tiles_list, tile_index, tipe):

        # if tile_index == 1:
        #     position = position_1_start
        # elif tile_index == 2:
        #     position = position_2_start

        tiles_list = []

        # for tile in double_tiles_list:
        #     if tile_index == 1:
        #         position_start = tile.position_1_start
        #     elif tile_index == 2:
        #         position_start = tile.position_2_start
        #     else:
        #         position_start = 0
        #     match_length = position_start + tile.match_length - 1
        #     tiles_list.append([position_start, match_length])

        if tile_index == 1:
            for tile in double_tiles_list:
                position_start = tile.position_1_start
                match_length = position_start + tile.match_length - 1
                tiles_list.append([position_start, match_length])
        elif tile_index == 2:
            for tile in double_tiles_list:
                position_start = tile.position_2_start
                match_length = position_start + tile.match_length - 1
                tiles_list.append([position_start, match_length])

        mapping_hash_list = []
        mapping_preprocess_list = []
        mapping_text_code_list = []
        mapping_doc_list = []
        
        for block in blocks:
            if block.mapping:
                if block.mapping.mapping_preprocess:
                    mapping_hash_list.append(block.mapping.mapping_hash)
                    mapping_preprocess_list.append(block.mapping.mapping_preprocess)
                    mapping_text_code_list.append(block.mapping.mapping_text_code)
                    mapping_doc_list.append(block.mapping.mapping_doc)

        # print(len(mapping_hash_list))
        # print(len(mapping_preprocess_list))
        # print(len(mapping_text_code_list))
        # print(len(mapping_doc_list))
                

        list_match_hash_mapping = gst_tile_to_hash_map(mapping_hash_list, tiles_list)

        list_match_textcode_mapping = gst_hash_to_textcode_map(mapping_text_code_list, mapping_preprocess_list, list_match_hash_mapping)

        list_match_doc_mapping = gst_textcode_to_doc_map(list_match_textcode_mapping, mapping_doc_list, tipe)
        # if tile_index == 1 and tipe == "TEXT":
            # print(mapping_hash_list)
            # print(mapping_preprocess_list)
            # print(mapping_doc_list)
        # print(tiles_list)

        idx = 0

        for block in blocks:
            if block.mapping.mapping_preprocess:
                block.match_doc_mapping = list_match_doc_mapping[idx]
                idx +=1

        # print(idx)
        
        return blocks

    
    