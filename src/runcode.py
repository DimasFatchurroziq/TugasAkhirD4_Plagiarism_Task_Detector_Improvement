import asyncio
from dependencies.factory import get_preprocess_service
from dependencies.factory import get_rollinghash_service
from dependencies.factory import get_fingerprint_service
from dependencies.factory import get_matching_service
from dependencies.factory import get_gst_service
from dependencies.factory import get_similarity_service

async def run_1(text):
    preprocessing_service = get_preprocess_service()
    character_list = await preprocessing_service.preprocessing_code(text)

    rollinghash_service = get_rollinghash_service()
    rollinghash_list = await rollinghash_service.rollinghash_text(character_list)

    winnowing_service = get_fingerprint_service()
    fingerprint_list = winnowing_service.winnowing(rollinghash_list, 4)

    return fingerprint_list, rollinghash_list
    
async def run_2(fingerprint_list_1, fingerprint_list_2, rollinghash_list_1, rollinghash_list_2):
    matching_service = get_matching_service()
    sort_matched_list = matching_service.matching(fingerprint_list_1, fingerprint_list_2)

    gst_service = get_gst_service()
    tiles_list, length_1, length_2 = gst_service.gst(sort_matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len=6)

    similarity_service = get_similarity_service()
    similarity = similarity_service.similarity(tiles_list, length_1, length_2)

    return similarity

import os
def read_file(filename):
    base_path = os.path.dirname(__file__)  # folder tempat file .py berada
    file_path = os.path.join(base_path, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    text_1 = read_file("runcode1.txt")
    text_2 = read_file("runcode2.txt")

    fingerprint_list_1, rollinghash_list_1 = asyncio.run(run_1(text_1))
    fingerprint_list_2, rollinghash_list_2 = asyncio.run(run_1(text_2))

    langkah2_1 = asyncio.run(run_2(fingerprint_list_1, fingerprint_list_2, rollinghash_list_1, rollinghash_list_2))

    print(langkah2_1)

