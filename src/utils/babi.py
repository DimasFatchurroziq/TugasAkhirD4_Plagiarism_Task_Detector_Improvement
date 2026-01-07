# def fingerprint(window_list):
#     fingerprint_list = []
    
#     # [hash, index]

#     # [[[1708, 0], [2271, 1], [2154, 2], [2317, 3]],   [[2271, 1], [2154, 2], [2317, 3], [2279, 4]]], 

#     # [[1708, 0], [2271, 3], [2154, 10], [2317, 12]]

#     for i in range(len(window_list)) :
        
#         if (i == 0) :
#             terkecil = window_list[i][0]
#             for x in range(1, 3) :
#                 if (window_list[i][x][0] < terkecil[0]) :
#                     terkecil = window_list[i][x]
#             fingerprint_list.append(terkecil) 

#             index_list = 0  
#             print(1, index_list) 

#         else :
#             if (window_list[i][3][1] - fingerprint_list[index_list][1] < 4):

#                 terkecil = fingerprint_list[index_list] 
                
#                 if (window_list[i][3][0] <= terkecil[0]) :
#                     terkecil = window_list[i][3]
#                     fingerprint_list.append(terkecil)
#                     index_list += 1
                
#                 print(2, index_list)

#             else: #>=4
#                 terkecil = window_list[i][0]
#                 for x in range(1, 3) :
#                     if (window_list[i][x][0] < terkecil[0]) :
#                         terkecil = window_list[i][x]
#                 fingerprint_list.append(terkecil)
#                 index_list += 1

#                 print(3, index_list)

#     return fingerprint_list


# if __name__ == "__main__":
#     window_list = [[[1708, 0], [2271, 1], [2154, 2], [2317, 3]], [[2271, 1], [2154, 2], [2317, 3], [2279, 4]], [[2154, 2], [2317, 3], [2279, 4], [2180, 5]], [[2317, 3], [2279, 4], [2180, 5], [2288, 6]], [[2279, 4], [2180, 5], [2288, 6], [1838, 7]]]
#     babi = fingerprint(window_list)
#     print(babi)




def greedy_string_tiling(text_a, text_b, min_match_len=3):
    tiles = []
    max_match = min_match_len + 1
    
    # Penanda untuk karakter yang sudah dipakai
    marked_a = [False] * len(text_a)
    marked_b = [False] * len(text_b)

    while max_match > min_match_len:
        max_match = min_match_len
        matches = []

        # Cari kecocokan terpanjang yang tersedia
        for i in range(len(text_a)):
            for j in range(len(text_b)):
                k = 0
                # Hitung panjang kecocokan selama karakter sama dan belum ditandai
                while (i + k < len(text_a) and j + k < len(text_b) and
                       text_a[i + k] == text_b[j + k] and
                       not marked_a[i + k] and not marked_b[j + k]):
                    k += 1
                
                if k > max_match:
                    max_match = k
                    matches = [(i, j, k)]
                elif k == max_match and k > min_match_len:
                    matches.append((i, j, k))

        # Tandai (Marking) kecocokan yang ditemukan
        for i, j, k in matches:
            # Cek ulang apakah masih bisa ditandai (menghindari tumpang tindih)
            if not any(marked_a[i + x] for x in range(k)) and \
               not any(marked_b[j + x] for x in range(k)):
                for x in range(k):
                    marked_a[i + x] = True
                    marked_b[j + x] = True
                tiles.append((i, j, k))

    return tiles

# Contoh Penggunaan:
a = "algoritma greedy string tiling"
# a = "abcdefghij strin"
b = "string tiling menggunakan algoritma greedy"
hasil = greedy_string_tiling(a, b, 5)

print(f"Tiles ditemukan: {hasil}")
# Output akan menunjukkan posisi dan panjang blok 'algoritma greedy' dan 'string tiling'

