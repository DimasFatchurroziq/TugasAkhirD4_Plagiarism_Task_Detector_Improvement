from src.utils.ngrams_generate import generate_ngrams

def test_generate():
    tokens_list = ['Indonesia', 'adalah', 'negara', 'yang', 'besar', '.']
    result = generate_ngrams(tokens_list, 2)
    assert result == [['Indonesia', 'adalah'], ['adalah', 'negara'], ['negara', 'yang'], ['yang', 'besar'], ['besar', '.']]

def test_generate_ngrams():
    tokens_list = ['I', 'n', 'd', 'o', 'n', 'e', 's', 'h', ' ', '.']
    result = generate_ngrams(tokens_list, 3)
    assert result == [['I', 'n', 'd'], ['n', 'd', 'o'], ['d', 'o', 'n'], ['o', 'n', 'e'], ['n', 'e', 's'], ['e', 's', 'h'], ['s', 'h', ' '], ['h', ' ', '.']]