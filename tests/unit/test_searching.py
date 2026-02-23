from src.infrastructures.rkr_gst.searching import binary_search

def test_binary_search_find_match():
    """Menguji pencarian jika data ditemukan"""
    # Data: [urutan, nilai] -> Diurutkan berdasarkan nilai (indeks 1)
    sorted_list = [[0, 1838], [1, 2271], [2, 2154]]
    sorted_list.sort(key=lambda x: x[1]) # Urut berdasarkan nilai: 1838, 2154, 2271
    
    target = [7, 1838] # Kita mencari nilai 1838 yang ada di target indeks 7
    index = 1 # Cari berdasarkan nilai (indeks 1 dari target)
    
    hasil = binary_search(sorted_list, target, index)
    
    # Ekspektasi: [7 (index target), 0 (index hasil), 1838 (nilai hasil)]
    assert hasil == [[7, 0, 1838]]

def test_binary_search_not_found():
    """Menguji jika data tidak ditemukan dalam list"""
    sorted_list = [[0, 1838], [1, 2271]]
    target = [5, 9999] # Nilai 9999 tidak ada
    index = 1
    
    hasil = binary_search(sorted_list, target, index)
    assert hasil == []

def test_binary_search_duplicate_logic():
    """Menguji perilaku fungsi saat ada data duplikat"""
    # Karena fungsi kamu menggunakan 'return' di dalam loop, 
    # ia hanya akan mengambil yang pertama ditemukan oleh bisect.
    sorted_list = [[0, 100], [1, 100], [2, 100]]
    target = [9, 100]
    index = 1
    
    hasil = binary_search(sorted_list, target, index)
    # Harus mengembalikan elemen pertama yang cocok dari slice 'matched'
    assert hasil == [[9, 0, 100], [9, 1, 100], [9, 2, 100]]
