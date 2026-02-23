from src.infrastructures.rollinghash.ngrams_generate import generate_ngrams
import pytest

#teks biasa
def test_generate_ngrams_basic():
    tokens_list = ['Indonesia', 'adalah', 'negara', 'yang', 'besar', '.']
    result = generate_ngrams(tokens_list, 2)
    expected = [
        ['Indonesia', 'adalah'],
        ['adalah', 'negara'],
        ['negara', 'yang'],
        ['yang', 'besar'],
        ['besar', '.']
    ]
    assert result == expected

def test_generate_ngrams_characters():
    tokens_list = ['I', 'n', 'd', 'o', 'n', 'e', 's', 'h', ' ', '.']
    result = generate_ngrams(tokens_list, 3)
    expected = [
        ['I', 'n', 'd'],
        ['n', 'd', 'o'],
        ['d', 'o', 'n'],
        ['o', 'n', 'e'],
        ['n', 'e', 's'],
        ['e', 's', 'h'],
        ['s', 'h', ' '],
        ['h', ' ', '.']
    ]
    assert result == expected

def test_generate_ngrams_n_equals_1():
    tokens_list = ['A', 'B', 'C']
    result = generate_ngrams(tokens_list, 1)
    expected = [['A'], ['B'], ['C']]
    assert result == expected

def test_generate_ngrams_n_equals_list_length():
    tokens_list = ['Hello', 'World']
    result = generate_ngrams(tokens_list, 2)
    expected = [['Hello', 'World']]
    assert result == expected

def test_generate_ngrams_n_larger_than_list():
    tokens_list = ['Hello', 'World']
    result = generate_ngrams(tokens_list, 3)
    expected = []
    assert result == expected

def test_generate_ngrams_empty_list():
    tokens_list = []
    result = generate_ngrams(tokens_list, 2)
    expected = []
    assert result == expected

@pytest.mark.parametrize(
    "tokens_list, n, expected",
    [
        (['a', 'b', 'c', 'd'], 2, [['a','b'],['b','c'],['c','d']]),
        (['I','love','AI'], 3, [['I','love','AI']]),
        (['1','2','3','4','5'], 4, [['1','2','3','4'],['2','3','4','5']]),
        (['x'], 1, [['x']])
    ]
)
def test_generate_ngrams_parametrized(tokens_list, n, expected):
    assert generate_ngrams(tokens_list, n) == expected


#kode program
def test_generate_ngrams_code_python_words():
    tokens_list = ['def', 'add', '(', 'a', ',', 'b', ')', ':', 'return', 'a', '+', 'b']
    result = generate_ngrams(tokens_list, 2)
    expected = [
        ['def', 'add'], ['add', '('], ['(', 'a'], ['a', ','], [',', 'b'], 
        ['b', ')'], [')', ':'], [':', 'return'], ['return', 'a'], ['a', '+'], ['+', 'b']
    ]
    assert result == expected

def test_generate_ngrams_code_python_chars():
    tokens_list = list("def add(a, b): return a + b")
    result = generate_ngrams(tokens_list, 3)
    expected = [
        ['d','e','f'], ['e','f',' '], ['f',' ','a'], [' ','a','d'], ['a','d','d'],
        ['d','d','('], ['d','(','a'], ['(','a',','], ['a',',',' '], [',',' ','b'],
        [' ','b',')'], ['b',')',':'], [')',':',' '], [':',' ','r'], [' ','r','e'],
        ['r','e','t'], ['e','t','u'], ['t','u','r'], ['u','r','n'], ['r','n',' '],
        ['n',' ','a'], [' ','a',' '], ['a',' ','+'], [' ','+',' '], ['+',' ','b']
    ]
    assert result == expected

def test_generate_ngrams_code_js_words():
    tokens_list = ['function', 'sum', '(', 'x', ',', 'y', ')', '{', 'return', 'x', '+', 'y', ';', '}']
    result = generate_ngrams(tokens_list, 2)
    expected = [
        ['function','sum'], ['sum','('], ['(','x'], ['x',','], [',','y'], ['y',')'], [')','{'], ['{','return'],
        ['return','x'], ['x','+'], ['+','y'], ['y',';'], [';','}']
    ]
    assert result == expected
