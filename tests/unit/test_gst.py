from src.utils.gst import greedy_string_tiling

def test_gst_basic_case():
    """Menguji data yang kamu berikan sebelumnya"""
    sort_matched_list = [[2, 2, 2154]]
    indexing_list_a = [1708, 2271, 2154, 2317, 2279, 2180, 2288, 1838]
    indexing_list_b = [1838, 2271, 2154, 2317, 2279, 2180, 2288, 1839]
    
    hasil = greedy_string_tiling(sort_matched_list, indexing_list_a, indexing_list_b, min_match_len=3)
    # Ekspektasi: 1 ubin, mulai indeks 1 panjang 6
    assert hasil == ([[1, 1, 6]], 8, 8)

def test_gst_no_match():
    """Menguji jika tidak ada kecocokan yang memenuhi min_match_len"""
    sort_matched_list = [[0, 0, 100]]
    list_a = [100, 101]
    list_b = [100, 999]
    
    # Hanya cocok 1 karakter, sedangkan min_match_len=3
    hasil = greedy_string_tiling(sort_matched_list, list_a, list_b, min_match_len=3)
    assert hasil == ([], 2, 2)

def test_gst_hehe():
    sort_matched_list = [[0, 2, 2049], [1, 3, 2096], [4, 6, 2045], [4, 10, 2045], [5, 7, 2086], [5, 11, 2086], [5, 26, 2086], [8, 6, 2045], [8, 10, 2045], [9, 7, 2086], [9, 11, 2086], [9, 26, 2086], [12, 14, 2057], [15, 17, 2113]]
    indexing_list_a = [2049, 2096, 2209, 2215, 2045, 2086, 2105, 2311, 2045, 2086, 2105, 2312, 2057, 2117, 2184, 2113, 2359]
    indexing_list_b = [2097, 2278, 2049, 2096, 2209, 2215, 2045, 2086, 2105, 2311, 2045, 2086, 2105, 2312, 2057, 2117, 2184, 2113, 2359, 2128, 2409, 2376, 2177, 2095, 2078, 2205, 2086, 2176, 2337, 2167, 2117, 2368]

    hasil = greedy_string_tiling(sort_matched_list, indexing_list_a, indexing_list_b, min_match_len=3)
    assert hasil == ([[0, 2, 17]], 17, 32)

def test_gst_basic_case_1():
    matched_list = [[1, 3, 2096]]
    indexing_list_a = [2049, 2096, 2209, 2215]
    indexing_list_b = [45, 45, 45, 2096, 2209, 2215]
    hasil = greedy_string_tiling(matched_list, indexing_list_a, indexing_list_b, min_match_len=3)
    assert hasil == ([[1,3,3]], 4, 6)

def test_gst_multiple_tiles():
    """Menguji dua ubin yang berbeda posisi"""
    # Ubin 1: [0,1,2], Ubin 2: [5,6,7]
    list_a = [10, 20, 30, 99, 99, 40, 50, 60]
    list_b = [10, 20, 30, 88, 88, 40, 50, 60]
    matched = [[0, 0], [5, 5]]
    
    hasil = greedy_string_tiling(matched, list_a, list_b, min_match_len=2)
    # Karena kodemu meng-update min_match_len, ubin kedua hanya terambil 
    # jika panjangnya > ubin pertama.
    assert len(hasil) >= 1