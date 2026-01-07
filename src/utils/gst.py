def greedy_string_tiling(matched_list, indexing_list_a, indexing_list_b, min_match_len=3):
    tiles = []
    index_tile = 0
    
    for i in range(len(matched_list)) :

        a = matched_list[i][0]
        b = matched_list[i][1]

        if tiles and tiles[index_tile-1][0] <= a and a <= tiles[index_tile-1][0] + tiles[index_tile-1][2]:
            continue

        else :
            k = 0 #kanan
            while (a + 1 + k < len(indexing_list_a) and b + 1 + k < len(indexing_list_b) and
                indexing_list_a[a + 1 + k] == indexing_list_b[b + 1 + k]):
                k += 1

            l = 0 #kiri     
            while (a - 1 - l >= 0 and b - 1 - l >= 0 and
                    indexing_list_a[a - 1 - l] == indexing_list_b[b - 1 - l]):
                l += 1

            long_tile = k + l + 1
            if long_tile > min_match_len:
                limit_start_a = a - l
                limit_start_b = b - l
                tiles.append([limit_start_a, limit_start_b, long_tile])
                index_tile += 1

    return tiles

