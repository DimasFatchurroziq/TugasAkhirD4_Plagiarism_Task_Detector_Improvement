from src.utils.sorting import timsort
import pytest

def test_sort_by_first_index():
    data = [
        [3, "c"],
        [1, "a"],
        [2, "b"]
    ]
    result = timsort(data, 0)
    expected = [
        [1, "a"],
        [2, "b"],
        [3, "c"]
    ]
    assert result == expected


def test_sort_by_second_index():
    data = [
        [1, "c"],
        [2, "a"],
        [3, "b"]
    ]
    result = timsort(data, 1)
    expected = [
        [2, "a"],
        [3, "b"],
        [1, "c"]
    ]
    assert result == expected


def test_sort_with_duplicate_values():
    data = [
        [1, "b"],
        [2, "a"],
        [3, "a"]
    ]
    result = timsort(data, 1)
    expected = [
        [2, "a"],
        [3, "a"],
        [1, "b"]
    ]
    assert result == expected


def test_empty_list():
    data = []
    result = timsort(data, 0)
    assert result == []


def test_single_element():
    data = [[1, "a"]]
    result = timsort(data, 0)
    assert result == [[1, "a"]]

def test_sort_by_id():
    data = [
        [3, "Charlie", 88],
        [1, "Alice", 90],
        [2, "Bob", 85],
    ]

    result = timsort(data, 0)

    expected = [
        [1, "Alice", 90],
        [2, "Bob", 85],
        [3, "Charlie", 88],
    ]

    assert result == expected


def test_sort_by_name():
    data = [
        [1, "Charlie", 88],
        [2, "Alice", 90],
        [3, "Bob", 85],
    ]

    result = timsort(data, 1)

    expected = [
        [2, "Alice", 90],
        [3, "Bob", 85],
        [1, "Charlie", 88],
    ]

    assert result == expected


def test_sort_by_score():
    data = [
        [1, "Alice", 90],
        [2, "Bob", 85],
        [3, "Charlie", 88],
    ]

    result = timsort(data, 2)

    expected = [
        [2, "Bob", 85],
        [3, "Charlie", 88],
        [1, "Alice", 90],
    ]

    assert result == expected

def test_sort_four_elements():
    data = [
        [1, "A", 90, "active"],
        [2, "B", 85, "inactive"],
        [3, "C", 88, "active"],
    ]

    result = timsort(data, 3)

    expected = [
        [1, "A", 90, "active"],
        [3, "C", 88, "active"],
        [2, "B", 85, "inactive"],
    ]

    assert result == expected

def test_sort_by_hash_value():
    data = [
        [0, 2266],
        [1, 2332],
        [2, 2340],
        [5, 2320],
        [7, 2290],
        [8, 2098],
        [11, 2095],
    ]

    result = timsort(data, 1)

    expected = [
        [11, 2095],
        [8, 2098],
        [0, 2266],
        [7, 2290],
        [5, 2320],
        [1, 2332],
        [2, 2340],
    ]

    assert result == expected


def test_sort_by_index():
    data = [
        [5, 2320],
        [0, 2266],
        [11, 2095],
        [2, 2340],
    ]

    result = timsort(data, 0)

    expected = [
        [0, 2266],
        [2, 2340],
        [5, 2320],
        [11, 2095],
    ]

    assert result == expected

def test_sort_with_duplicate_hash():
    data = [
        [0, 100],
        [1, 100],
        [2, 90],
    ]

    result = timsort(data, 1)

    expected = [
        [2, 90],
        [0, 100],
        [1, 100],
    ]

    assert result == expected

def test_sort_by_hash():
    data = [
        [0, 2266, 0.91, 1700000001],
        [1, 2332, 0.88, 1700000002],
        [2, 2340, 0.95, 1700000003],
        [5, 2320, 0.89, 1700000004],
        [7, 2290, 0.92, 1700000005],
    ]

    result = timsort(data, 1)

    expected = [
        [0, 2266, 0.91, 1700000001],
        [7, 2290, 0.92, 1700000005],
        [5, 2320, 0.89, 1700000004],
        [1, 2332, 0.88, 1700000002],
        [2, 2340, 0.95, 1700000003],
    ]

    assert result == expected


def test_sort_by_score():
    data = [
        [0, 2266, 0.91, 1700000001],
        [1, 2332, 0.88, 1700000002],
        [2, 2340, 0.95, 1700000003],
        [5, 2320, 0.89, 1700000004],
    ]

    result = timsort(data, 2)

    expected = [
        [1, 2332, 0.88, 1700000002],
        [5, 2320, 0.89, 1700000004],
        [0, 2266, 0.91, 1700000001],
        [2, 2340, 0.95, 1700000003],
    ]

    assert result == expected


def test_sort_by_timestamp():
    data = [
        [2, 2340, 0.95, 1700000003],
        [0, 2266, 0.91, 1700000001],
        [1, 2332, 0.88, 1700000002],
    ]

    result = timsort(data, 3)

    expected = [
        [0, 2266, 0.91, 1700000001],
        [1, 2332, 0.88, 1700000002],
        [2, 2340, 0.95, 1700000003],
    ]

    assert result == expected

@pytest.mark.parametrize(
    "n,expected",
    [
        (0, [
            [0, 2266, 0.91, 1700000001],
            [1, 2332, 0.88, 1700000002],
            [2, 2340, 0.95, 1700000003],
            [5, 2320, 0.89, 1700000004],
        ]),
        (1, [
            [0, 2266, 0.91, 1700000001],
            [5, 2320, 0.89, 1700000004],
            [1, 2332, 0.88, 1700000002],
            [2, 2340, 0.95, 1700000003],
        ]),
    ],
)
def test_sort_parametrized(n, expected):
    data = [
        [5, 2320, 0.89, 1700000004],
        [0, 2266, 0.91, 1700000001],
        [1, 2332, 0.88, 1700000002],
        [2, 2340, 0.95, 1700000003],
    ]

    assert timsort(data, n) == expected
