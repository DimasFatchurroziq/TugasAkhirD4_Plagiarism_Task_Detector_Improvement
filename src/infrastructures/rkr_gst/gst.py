from src.utils.sorting import longest_sort

def gst_right_left(sort_matched_list, rollinghash_list_1, rollinghash_list_2, min_match_len):
    double_tiles = []
    index_tile = 0
    length_1 = len(rollinghash_list_1)
    length_2 = len(rollinghash_list_2)
    
    for i in range(len(sort_matched_list)) :
        # print("asi")

        a = sort_matched_list[i][0]
        b = sort_matched_list[i][1]

        if double_tiles and double_tiles[index_tile-1][0] <= a and a <= double_tiles[index_tile-1][0] + double_tiles[index_tile-1][2]:
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
                double_tiles.append([limit_start_1, limit_start_2, long_tile])
                index_tile += 1
                # print("5")

    return double_tiles, length_1, length_2


def gst_tile_to_hash_map(mapping_hash_list, tiles_list):

    indexed_tiles = list(enumerate(tiles_list))

    indexed_tiles = sorted(
        indexed_tiles,
        key=lambda x: x[1][1] - x[1][0],
        reverse=True
    )

    list_match_hash_mapping = []

    for mapping_idx, (m_start, m_end) in enumerate(mapping_hash_list):

        segments = [[m_start, m_end, "FREE", None]]

        for tile_id, (d_start, d_end) in indexed_tiles:

            new_segments = []

            for seg_start, seg_end, label, source in segments:

                if seg_start > seg_end:
                    continue

                if label == "MATCHED":

                    new_segments.append([
                        seg_start,
                        seg_end,
                        label,
                        source
                    ])
                    continue

                if d_end < seg_start or d_start > seg_end:

                    new_segments.append([
                        seg_start,
                        seg_end,
                        label,
                        source
                    ])

                else:

                    # kiri
                    if seg_start < d_start:

                        left_start = seg_start
                        left_end = d_start - 1

                        if left_start <= left_end:
                            new_segments.append([
                                left_start,
                                left_end,
                                "FREE",
                                None
                            ])

                    # overlap
                    overlap_start = max(seg_start, d_start)
                    overlap_end = min(seg_end, d_end)

                    if overlap_start <= overlap_end:
                        new_segments.append([
                            overlap_start,
                            overlap_end,
                            "MATCHED",
                            tile_id
                        ])

                    # kanan
                    if seg_end > d_end:

                        right_start = d_end + 1
                        right_end = seg_end

                        if right_start <= right_end:
                            new_segments.append([
                                right_start,
                                right_end,
                                "FREE",
                                None
                            ])

            segments = new_segments

        local = []

        for s, e, label, source in segments:

            if s <= e:
                local.append({
                    "label": label,
                    "start": s - m_start,
                    "end": e - m_start,
                    "tile_source": source,
                    "mapping_idx": mapping_idx
                })

        has_matched = any(item["label"] == "MATCHED" for item in local)
      
        is_detect_value = True if has_matched else False

        list_match_hash_mapping.append({
            "is_detect": is_detect_value,
            "block": local
        })

    return list_match_hash_mapping


def gst_hash_to_textcode_map(mapping_text_code_list, mapping_process_list, list_match_hash_mapping):
    list_match_textcode_mapping = []

    for m_idx, group in enumerate(list_match_hash_mapping):
        mapped_group = []

        for item in group["block"]:

            # map_process_start = mapping_process_list[m_idx][item["start"]]
            
            map_process_start = mapping_process_list[m_idx][item["start"]]

            map_process_end   = mapping_process_list[m_idx][item["end"]]

            start_range = mapping_text_code_list[m_idx][0]
            end_range   = mapping_text_code_list[m_idx][1]

            map_text_code_start = find_in_range(start_range, end_range, map_process_start)
            map_text_code_end = find_in_range(start_range, end_range, map_process_end)

            mapped_group.append({
                "label": item["label"],
                "start": map_text_code_start,
                "end": map_text_code_end,
                "tile_source": item["tile_source"],
                "mapping_idx": m_idx # Tetap kita masukkan m_idx hasil enumerate agar output konsisten
            })

        list_match_textcode_mapping.append({
            "is_detect": group["is_detect"],
            "block": mapped_group
        })

    return list_match_textcode_mapping



def gst_textcode_to_doc_map(list_match_textcode_mapping, mapping_doc_list, tipe):
    list_match_doc_mapping = []

    for m_idx, group in enumerate(list_match_textcode_mapping):
        converted_group = []

        target_list = mapping_doc_list[m_idx]

        for item in group["block"]:
            rel_start = item["start"]
            rel_end = item["end"]

            actual_start = target_list[rel_start] if 0 <= rel_start < len(target_list) else -1
            actual_end = target_list[rel_end] if 0 <= rel_end < len(target_list) else -1

            converted_group.append({
                "type": tipe,
                "label": item["label"],
                "start": actual_start,
                "end": actual_end,
                "tile_source": item["tile_source"],
                "mapping_idx": m_idx
            })

        list_match_doc_mapping.append({
            "is_detect": group["is_detect"],
            "block": converted_group
        })

    return list_match_doc_mapping


def find_in_range(start, end, target):
    if start <= target <= end:
        return target - start
    return -1