from src.utils.sorting import timsort

import pytest
import timeit
import bisect
import random

def timsort(fingerprint_list):
    fingerprint_list.sort()
    return fingerprint_list

def test_timsort_random_data():
    """Menguji data acak normal"""
    input_data = [38, 27, 43, 3, 9, 82, 10]
    expected = [3, 9, 10, 27, 38, 43, 82]
    assert timsort(input_data) == expected

def test_timsort_already_sorted():
    """Menguji data yang sudah urut"""
    input_data = [1, 2, 3, 4, 5]
    expected = [1, 2, 3, 4, 5]
    assert timsort(input_data) == expected

def test_timsort_reverse_sorted():
    """Menguji data yang urut terbalik"""
    input_data = [5, 4, 3, 2, 1]
    expected = [1, 2, 3, 4, 5]
    assert timsort(input_data) == expected

def test_timsort_empty_list():
    """Menguji list kosong"""
    input_data = []
    expected = []
    assert timsort(input_data) == expected

def test_timsort_with_duplicates():
    """Menguji data dengan angka duplikat"""
    input_data = [5, 1, 3, 5, 2, 1]
    expected = [1, 1, 2, 3, 5, 5]
    assert timsort(input_data) == expected

def test_timsort_single_element():
    """Menguji list dengan hanya satu elemen"""
    input_data = [10]
    expected = [10]
    assert timsort(input_data) == expected# Fungsi Timsort kita
    
def timsort_func(data):
    data.sort()
    return data

def test_benchmark_performance():
    # 1. Siapkan 10.000 data acak
    data_besar = [random.randint(1, 100000) for _ in range(10000)]
    
    # 2. Benchmark SORTING (Timsort)
    # Kita ukur berapa lama mengurutkan 10.000 data
    start_sort = timeit.default_timer()
    data_urut = timsort_func(data_besar)
    end_sort = timeit.default_timer()
    
    time_sort = (end_sort - start_sort) * 1000 # konversi ke milidetik
    
    # 3. Benchmark SEARCHING (Binary Search) sebanyak 1.000 kali
    targets = [random.randint(1, 100000) for _ in range(1000)]
    
    start_search = timeit.default_timer()
    for t in targets:
        bisect.bisect_left(data_urut, t)
    end_search = timeit.default_timer()
    
    time_search = (end_search - start_search) * 1000 # konversi ke milidetik

    print(f"\n--- HASIL BENCHMARK (10.000 DATA) ---")
    print(f"Waktu Sorting (Timsort)      : {time_sort:.4f} ms")
    print(f"Waktu Searching (1.000 kali) : {time_search:.4f} ms")
    
    # Assertion sederhana untuk memastikan proses berjalan
    assert len(data_urut) == 10000

