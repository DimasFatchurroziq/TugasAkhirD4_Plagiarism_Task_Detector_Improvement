def greedy_string_tiling(sort_matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len):
    tiles = []
    index_tile = 0
    length_1 = len(rollinghash_list_1)
    length_2 = len(rollinghash_list_2)
    
    for i in range(len(sort_matched_list)) :
        # print("asi")

        a = sort_matched_list[i][0]
        b = sort_matched_list[i][1]

        if tiles and tiles[index_tile-1][0] <= a and a <= tiles[index_tile-1][0] + tiles[index_tile-1][2]:
            # print("1")
            continue

        else :
            # print("2", a, b)
            k = 0 #kanan
            # print(a + 1 + k, b + 1 + k, rollinghash_list_1[a + 1 + k][1], rollinghash_list_2[b + 1 + k][1])
            # print(rollinghash_list_1)
            # print(rollinghash_list_2)
            while (a + 1 + k < length_1 and b + 1 + k < length_2 and
                rollinghash_list_1[a + 1 + k] == rollinghash_list_2[b + 1 + k]):
                k += 1
                # print("3")

            l = 0 #kiri     
            while (a - 1 - l >= 0 and b - 1 - l >= 0 and
                    rollinghash_list_1[a - 1 - l] == rollinghash_list_2[b - 1 - l]):
                l += 1
                # print("4")

            long_tile = k + l + 1
            if long_tile >= min_match_len:
                limit_start_1 = a - l
                limit_start_2 = b - l
                tiles.append([limit_start_1, limit_start_2, long_tile])
                index_tile += 1
                # print("5")

    return tiles, length_1, length_2

if __name__ == "__main__":
    asu = [[0, 2097], [1, 2278], [2, 2049], [3, 2096], [4, 2209], [5, 2215], [6, 2045], [7, 2086], [8, 2105], [9, 2311], [10, 2045], [11, 2086], [12, 2105], [13, 2312], [14, 2057], [15, 2117], [16, 2184], [17, 2113], [18, 2359], [19, 2128], [20, 2409], [21, 2376], [22, 2177], [23, 2095], [24, 2078], [25, 2205], [26, 2086], [27, 2176], [28, 2337], [29, 2167], [30, 2117], [31, 2368]]
    kontol = []
    for item in asu:
        kontol.append(item[1])

    print(kontol)

    # matched_list = [[1, 3, 2096]]
    # indexing_list_a = [2049, 2096, 2209, 2215]
    # indexing_list_b = [45, 45, 45, 2096, 2209, 2215]

    # tiles, length_1, length_2 = greedy_string_tiling(matched_list, indexing_list_a, indexing_list_b, min_match_len=3)

    # print(kontol)

