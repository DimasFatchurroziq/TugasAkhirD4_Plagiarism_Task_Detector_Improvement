from src.infrastructures.rolling_hash.rollinghash_generate import rollinghash_text

#teks biasa
def test_rollinghash_text():
    ngrams_list = [['I', 'n', 'd'], ['n', 'd', 'o'], ['d', 'o', 'n'], ['o', 'n', 'e'], ['n', 'e', 's'], ['e', 's', 'h'], ['s', 'h', ' '], ['h', ' ', '.']]
    assert rollinghash_text(ngrams_list) == [1708, 2271, 2154, 2317, 2279, 2180, 2288, 1838]

def test_rollinghash_long_text():
    ngrams_list = [['Indonesia', 'adalah'], ['adalah', 'negara'], ['negara', 'yang'], ['yang', 'besar'], ['besar', '.']]
    assert rollinghash_text(ngrams_list) == [29272660204, 546373369, 37691247, 10109030, 135622]

def test_rollinghash_special_text():
    ngrams_list = [['A'], ['B'], ['C'], ['1'], ['2'], ['3']]
    assert rollinghash_text(ngrams_list) == [65, 66, 67, 49, 50, 51]

#kode program
def test_rollinghash_code():
    ngrams_list = [['d','e','f'], ['e','f',' '], ['f',' ','a'], [' ','a','d'], ['a','d','d'], ['d','d','('], ['d','(','a'], ['(','a',','], ['a',',',' '], [',',' ','b'], [' ','b',')'], ['b',')',':'], [')',':',' '], [':',' ','r'], [' ','r','e'], ['r','e','t'], ['e','t','u'], ['t','u','r'], ['u','r','n'], ['r','n',' '], ['n',' ','a'], [' ','a',' '], ['a',' ','+'], [' ','+',' '], ['+',' ','b']]
    assert rollinghash_text(ngrams_list) == [2106, 2056, 1857, 1000, 2052, 2040, 1857, 1072, 1760, 930, 945, 1790, 920, 1170, 1069, 2344, 2197, 2438, 2438, 2296, 1985, 932, 1723, 716, 914]

def test_rollinghash_long_code():
    ngrams_list = [['function','sum'], ['sum','('], ['(','x'], ['x',','], [',','y'], ['y',')'], [')','{'], ['{','return'], ['return','x'], ['x','+'], ['+','y'], ['y',';'], [';','}']]
    assert rollinghash_text(ngrams_list) == [147077105, 9708, 280, 524, 297, 525, 287, 656262, 609936, 523, 293, 543, 361]

def test_rollinghash_long_code_2():
    ngrams_list = [['def', 'add'], ['add', '('], ['(', 'a'], ['a', ','], [',', 'b'], ['b', ')'], [')', ':'], [':', 'return'], ['return', 'a'], ['a', '+'], ['+', 'b']]
    assert rollinghash_text(ngrams_list) == [136836, 8248, 257, 432, 274, 433, 222, 390022, 609913, 431, 270]