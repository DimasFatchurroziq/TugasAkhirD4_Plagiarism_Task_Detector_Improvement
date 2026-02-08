from src.utils.fingerprint_generate import fingerprint_generate

def test_generate_fingerprint_window_4():
    window_list = [
        [[0, 1708], [1, 2271], [2, 2154], [3, 2317]],
        [[1, 2271], [2, 2154], [3, 2317], [4, 2279]],
        [[2, 2154], [3, 2317], [4, 2279], [5, 2180]],
        [[3, 2317], [4, 2279], [5, 2180], [6, 2288]],
        [[4, 2279], [5, 2180], [6, 2288], [7, 1838]],
    ]

    result = fingerprint_generate(window_list)

    assert result == [
        [0, 1708],
        [2, 2154],
        [5, 2180],
        [7, 1838],
    ]

def test_generate_fingerprint_window_3():
    window_list = [
        [[0, 3000], [1, 2100], [2, 2500]],
        [[1, 2100], [2, 2500], [3, 2000]],
        [[2, 2500], [3, 2000], [4, 2400]],
        [[3, 2000], [4, 2400], [5, 2300]],
    ]

    result = fingerprint_generate(window_list)

    assert result == [
        [1, 2100],
        [3, 2000],
    ]

def test_generate_fingerprint_window_5():
    window_list = [
        [[0, 4000], [1, 3500], [2, 3600], [3, 3400], [4, 3800]],
        [[1, 3500], [2, 3600], [3, 3400], [4, 3800], [5, 3300]],
        [[2, 3600], [3, 3400], [4, 3800], [5, 3300], [6, 3700]],
    ]

    result = fingerprint_generate(window_list)

    assert result == [
        [3, 3400],
        [5, 3300],
    ]

def test_generate_fingerprint_window_1():
    window_list = [
        [[0, 1000]],
        [[1, 900]],
        [[2, 800]],
        [[3, 700]],
    ]

    result = fingerprint_generate(window_list)

    assert result == [
        [0, 1000],
        [1, 900],
        [2, 800],
        [3, 700],
    ]

def test_generate_fingerprint_same_hash_choose_rightmost():
    window_list = [
        [[0, 1000], [1, 500], [2, 500]],
        [[1, 500], [2, 500], [3, 700]],
    ]

    result = fingerprint_generate(window_list)

    assert result == [
        [2, 500],
    ]
