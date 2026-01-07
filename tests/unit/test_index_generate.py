from src.utils.index_generate import generate_index

def test_generate_index():
    list = [1708, 2271, 2154, 2317, 2279, 2180, 2288, 1838]
    result = generate_index(list)
    assert result == [[0, 1708], [1, 2271], [2, 2154], [3, 2317], [4, 2279], [5, 2180], [6, 2288], [7, 1838]]