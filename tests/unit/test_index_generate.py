from src.utils.index_generate import generate_index

def test_generate_index():
    list = [1708, 2271, 2154, 2317, 2279, 2180, 2288, 1838]
    result = generate_index(list)
    assert result == [[1708, 0], [2271, 1], [2154, 2], [2317, 3], [2279, 4], [2180, 5], [2288, 6], [1838, 7]]