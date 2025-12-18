from src.utils.rollinghash_generate import rollinghash_text

def test_rollinghash_text():
    ngrams_list = [['I', 'n', 'd'], ['n', 'd', 'o'], ['d', 'o', 'n'], ['o', 'n', 'e'], ['n', 'e', 's'], ['e', 's', 'h'], ['s', 'h', ' '], ['h', ' ', '.']]
    result = rollinghash_text(ngrams_list)
    assert result == [1708, 2271, 2154, 2317, 2279, 2180, 2288, 1838]