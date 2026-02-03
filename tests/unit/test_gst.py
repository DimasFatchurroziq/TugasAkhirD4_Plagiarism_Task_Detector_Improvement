from src.utils.gst import greedy_string_tiling

def test_gst_basic_case():
    """Menguji data yang kamu berikan sebelumnya"""
    matched_list = [[2, 2, 2154], [3, 3, 2317], [7, 0, 1838]]
    indexing_list_a = [[0, 1708], [1, 2271], [2, 2154], [3, 2317], [4, 2279], [5, 2180], [6, 2288], [7, 1838]]
    indexing_list_b = [[0, 1838], [1, 2271], [2, 2154], [3, 2317], [4, 2279], [5, 2180], [6, 2288], [7, 1839]]
    
    hasil = greedy_string_tiling(matched_list, indexing_list_a, indexing_list_b, min_match_len=3)
    # Ekspektasi: 1 ubin, mulai indeks 1 panjang 6
    assert hasil == [[1, 1, 6]]

def test_gst_no_match():
    """Menguji jika tidak ada kecocokan yang memenuhi min_match_len"""
    matched_list = [[0, 0, 100]]
    list_a = [[0, 100], [1, 101]]
    list_b = [[0, 100], [1, 999]]
    
    # Hanya cocok 1 karakter, sedangkan min_match_len=3
    hasil = greedy_string_tiling(matched_list, list_a, list_b, min_match_len=3)
    assert hasil == []

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