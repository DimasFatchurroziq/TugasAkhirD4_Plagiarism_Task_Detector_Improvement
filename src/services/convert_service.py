from uuid import UUID
from collections import defaultdict
from typing import List, Dict
from src.models.model import Block, Rkrgst

from src.infrastructures.rkr_gst.gst import gst_tile_to_hash_map, gst_hash_to_textcode_map, gst_textcode_to_doc_map

class ConvertService:

    def __init__(self, compare_serv, 
        tahap8_serv, tahap9_serv, tahap10_serv,
        block_repo, compare_repo, rkrgst_repo
    ):
        self.compare_serv = compare_serv
        self.tahap8_serv = tahap8_serv
        self.tahap9_serv = tahap9_serv
        self.tahap10_serv = tahap10_serv
        self.block_repo = block_repo
        self.compare_repo = compare_repo
        self.rkrgst_repo = rkrgst_repo

    async def convert_html(self, comparison_id: UUID):

        comparison = await self.compare_serv.get_comparison(comparison_id)

        doc_1_id = comparison.document_1.id
        doc_2_id = comparison.document_2.id

        doc_1_path = comparison.document_1.path
        doc_2_path = comparison.document_2.path

        blocks_1 = await self.block_repo.get_by_doc_with_map(doc_1_id)
        blocks_by_type_1 = self.group_blocks_by_type(blocks_1)

        blocks_2 = await self.block_repo.get_by_doc_with_map(doc_2_id)
        blocks_by_type_2 = self.group_blocks_by_type(blocks_2)

        double_tiles_list = await self.rkrgst_repo.get_by_compare(comparison_id)
        rkrgsts_by_type = self.group_rkrgst_by_type(double_tiles_list)

        blocks_text_1 = self.tahap8_serv.reverse_map(blocks_by_type_1["TEXT"], rkrgsts_by_type["TEXT"], 1, "TEXT")
        blocks_code_1 = self.tahap8_serv.reverse_map(blocks_by_type_1["CODE"], rkrgsts_by_type["CODE"], 1, "CODE")

        blocks_text_2 = self.tahap8_serv.reverse_map(blocks_by_type_2["TEXT"], rkrgsts_by_type["TEXT"], 2, "TEXT")
        blocks_code_2 = self.tahap8_serv.reverse_map(blocks_by_type_2["CODE"], rkrgsts_by_type["CODE"], 2, "CODE")

        list_match_typing_mapping_1, list_match_image_mapping_1, list_image_content_1 = self.tahap9_serv.merge_and_ungroup(blocks_text_1, blocks_code_1, blocks_by_type_1["TERMINAL"])
        list_match_typing_mapping_2, list_match_image_mapping_2, list_image_content_2 = self.tahap9_serv.merge_and_ungroup(blocks_text_2, blocks_code_2, blocks_by_type_2["TERMINAL"])

        pages_data_1 = self.tahap10_serv.extract_pdf_to_data(doc_1_path, list_match_typing_mapping_1, list_match_image_mapping_1, list_image_content_1)
        pages_data_2 = self.tahap10_serv.extract_pdf_to_data(doc_2_path, list_match_typing_mapping_2, list_match_image_mapping_2, list_image_content_2)

        return pages_data_1, pages_data_2




    
    
    
    
    
    
    
    
    
    
    
    
    
    def group_blocks_by_type(self, blocks: List[Block]) -> Dict[str, List[Block]]:
        grouped = defaultdict(list)
        for block in blocks:
            grouped[block.type].append(block)
        return grouped

    def group_rkrgst_by_type(self, rkrgsts: List[Rkrgst]) -> Dict[str, List[Rkrgst]]:
        grouped = defaultdict(list)
        for rkr in rkrgsts:
            grouped[rkr.type].append(rkr)
        return grouped
    
    
    


