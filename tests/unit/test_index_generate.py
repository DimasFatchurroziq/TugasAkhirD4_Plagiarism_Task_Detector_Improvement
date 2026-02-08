from src.utils.index_generate import generate_index

def test_generate_index_normal():
    data = [1708, 2271, 2154, 2317, 2279, 2180, 2288, 1838]
    result = generate_index(data)

    assert result == [
        [0, 1708],
        [1, 2271],
        [2, 2154],
        [3, 2317],
        [4, 2279],
        [5, 2180],
        [6, 2288],
        [7, 1838],
    ]

def test_generate_index_single_element():
    data = [999]
    result = generate_index(data)

    assert result == [[0, 999]]

def test_generate_index_empty_list():
    data = []
    result = generate_index(data)

    assert result == []

def test_generate_index_duplicate_values():
    data = [100, 200, 200, 100]
    result = generate_index(data)

    assert result == [
        [0, 100],
        [1, 200],
        [2, 200],
        [3, 100],
    ]

def test_generate_index_negative_values():
    data = [-10, -5, 0, 5]
    result = generate_index(data)

    assert result == [
        [0, -10],
        [1, -5],
        [2, 0],
        [3, 5],
    ]
