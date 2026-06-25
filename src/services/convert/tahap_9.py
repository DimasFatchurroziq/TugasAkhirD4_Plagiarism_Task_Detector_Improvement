import heapq
from typing import Dict, List
from collections import defaultdict
from src.models.model import Block

class Tahap_9:

    def merge_and_ungroup(self, blocks_text, blocks_code, blocks_terminal):

        grouped_blocks = {}

        grouped_blocks["TEXT"] = blocks_text
        grouped_blocks["CODE"] = blocks_code
        grouped_blocks["TERMINAL"] = blocks_terminal

        # Mengambil semua list yang ada di dalam dictionary
        lists_to_merge = list(grouped_blocks.values())

        
        sorted_blocks = list(heapq.merge(*lists_to_merge, key=lambda block: block.sequence))

        blocks_by_source = self.group_blocks_by_source(sorted_blocks)
        
        list_match_typing_mapping = []
        # print(blocks_by_source["TYPING"])
        # for block in blocks_by_source["TYPING"]:
        #     print(block.__dict__)

        for block in blocks_by_source["TYPING"]:
            if hasattr(block, "match_doc_mapping"): 
                list_match_typing_mapping.append(block.match_doc_mapping)
        
        list_image_content = []
        list_match_image_mapping = []

        for block in blocks_by_source["IMAGE"]:
            list_image_content.append(block.content)
            if hasattr(block, "match_doc_mapping"): 
                list_match_image_mapping.append(block.match_doc_mapping)

        # print(len(list_match_typing_mapping))

        return list_match_typing_mapping, list_match_image_mapping, list_image_content




    def group_blocks_by_source(self, blocks: List[Block]) -> Dict[str, List[Block]]:
        grouped = defaultdict(list)
        for block in blocks:
            grouped[block.source].append(block)
        return grouped