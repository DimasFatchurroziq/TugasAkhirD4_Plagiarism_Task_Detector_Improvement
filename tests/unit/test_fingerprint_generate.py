from src.utils.fingerprint_generate import fingerprint_generate

def test_generate_fingerprint():
    window_list = [[[0, 1708], [1, 2271], [2, 2154], [3, 2317]], [[1, 2271], [2, 2154], [3, 2317], [4, 2279]], [[2, 2154], [3, 2317], [4, 2279], [5, 2180]], [[3, 2317], [4, 2279], [5, 2180], [6, 2288]], [[4, 2279], [5, 2180], [6, 2288], [7, 1838]]]
    result = fingerprint_generate(window_list)
    assert result == [[0, 1708], [2, 2154], [5, 2180], [7, 1838]]