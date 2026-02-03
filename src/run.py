import asyncio
from dependencies.factory import get_preprocess_service
from dependencies.factory import get_rollinghash_service
from dependencies.factory import get_fingerprint_service
from dependencies.factory import get_matching_service
from dependencies.factory import get_gst_service
from dependencies.factory import get_similarity_service

async def run_1(text):
    preprocessing_service = get_preprocess_service()
    character_list = await preprocessing_service.preprocessing_text(text)
    # print(character_list)

    rollinghash_service = get_rollinghash_service()
    rollinghash_list = await rollinghash_service.rollinghash_text(character_list)
    # print(rollinghash_list)

    winnowing_service = get_fingerprint_service()
    fingerprint_list = winnowing_service.winnowing(rollinghash_list, 4)
    # print(indexing_list)
    # print(fingerprint_list)

    return fingerprint_list, rollinghash_list
    
async def run_2(fingerprint_list_1, fingerprint_list_2, rollinghash_list_1, rollinghash_list_2):
    matching_service = get_matching_service()
    matched_list = matching_service.matching(fingerprint_list_1, fingerprint_list_2)
    # print(matched_list)

    gst_service = get_gst_service()
    tiles_list, length_1, length_2 = gst_service.gst(matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len=6)
    # print(tiles_list)

    similarity_service = get_similarity_service()
    similarity = similarity_service.similarity(tiles_list, length_1, length_2)

    return similarity

if __name__ == "__main__":
    # text_2 = "Apabila cara-cara di atas tidak berhasil"
    # text_2 = " cara-cara di atas tidak berhasil mengurangi keluhan nyeri punggung, sebaiknya periksakan diri Anda ke dokter saraf menggunakan asuransi kesehatan karyawan yang dimiliki. Dokter dapat melakukan beberapa pemeriksaan untuk memastikan diagnosis dan menentukan penyebab nyeri punggung bawah. Dokter akan melakukan pemeriksaan fisik, foto Rontgen, CT scan, dan MRI. Pada beberapa kasus, dokter juga mungkin akan menyarankan pemeriksaan EMG untuk mengevaluasi kondisi saraf punggung bawah. Setelah diagnosis dan penyebab nyeri punggung bawah diketahui, dokter baru dapat memberikan pengobatan yang sesuai. Berikut adalah pengobatan yang dapat diberikan dokter untuk mengatasi nyeri punggung bawah:"

    # text_1 = "abila cara-cara di atas"
    text_1 = "abila cara-cara di atas tidak berhasil mengurangi keluhan nyeri punggung, sebaiknya periksakan diri Anda ke dokter saraf menggunakan asuransi kesehatan karyawan yang dimiliki. Dokter dapat melakukan beberapa pemeriksaan untuk memastikan diagnosis dan menentukan penyebab nyeri punggung bawah. Dokter akan melakukan pemeriksaan fisik, foto Rontgen, CT scan, dan MRI. Pada beberapa kasus, dokter juga mungkin akan menyarankan pemeriksaan EMG untuk mengevaluasi kondisi saraf punggung bawah. Setelah diagnosis dan penyebab nyeri punggung bawah diketahui, dokter baru dapat memberikan pengobatan yang sesuai. Berikut adalah pengobatan yang dapat diberikan dokter untuk mengatasi nyeri punggung bawah:"
    text_2 = "Apabila cara-cara di atas tidak berhasil mengurangi keluhan nyeri punggung, sebaiknya periksakan diri Anda ke dokter saraf menggunakan asuransi kesehatan karyawan yang dimiliki. Dokter dapat melakukan beberapa pemeriksaan untuk memastikan diagnosis dan menentukan penyebab nyeri punggung bawah. Dokter akan melakukan pemeriksaan fisik, foto Rontgen, CT scan, dan MRI. Pada beberapa kasus, dokter juga mungkin akan menyarankan pemeriksaan EMG untuk mengevaluasi kondisi saraf punggung bawah. Setelah diagnosis dan penyebab nyeri punggung bawah diketahui, dokter baru dapat memberikan pengobatan yang sesuai. Berikut adalah pengobatan yang dapat diberikan dokter untuk mengatasi nyeri punggung bawah:"

    fingerprint_list_1, rollinghash_list_1 = asyncio.run(run_1(text_1))
    fingerprint_list_2, rollinghash_list_2 = asyncio.run(run_1(text_2))

    langkah2_1 = asyncio.run(run_2(fingerprint_list_1, fingerprint_list_2, rollinghash_list_1, rollinghash_list_2))

    print(langkah2_1)

