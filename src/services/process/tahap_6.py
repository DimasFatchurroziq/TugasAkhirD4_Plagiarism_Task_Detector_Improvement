from src.infrastructures.rkr_gst.gst import gst_tile_to_hash_map
from src.infrastructures.sentence_bert.sbert import embed_sentences
from src.infrastructures.preprocessing.text_tokenize import count_word


class Tahap_6:

    def embedding_sentence(self, blocks, double_tiles_list, tile_index, min_word_length, model):

        embedding_list = []

        tiles_list = []

        for item in double_tiles_list:
            position_start = item[tile_index]
            match_length = item[tile_index]+item[2]-1
            tiles_list.append([position_start, match_length])

        mapping_hash_list = []
        
        for block in blocks:
            if block.mapping:
                if block.mapping.mapping_hash:
                    mapping_hash_list.append(block.mapping.mapping_hash)

        list_match_hash_mapping = gst_tile_to_hash_map(mapping_hash_list, tiles_list)

        for order, group in enumerate(list_match_hash_mapping):

            if not group["is_detect"]:

                current_block = blocks[order]

                length_word = count_word(current_block.content)

                if length_word >= min_word_length:
                    if current_block.block_embedding:
                        block_id = current_block.id
                        embedding = current_block.block_embedding.embedding
                        embedding_list.append({
                            "is_exist": True,
                            "data": {
                                "block_id": block_id,
                                "embedding": embedding
                            }
                        })
                    else:
                        block_id = current_block.id
                        content = current_block.content
                        embedding = embed_sentences(content, model)
                        embedding_list.append({
                            "is_exist": False,
                            "data": {
                                "block_id": block_id,
                                "embedding": embedding
                            }
                        })

        return embedding_list
                


    