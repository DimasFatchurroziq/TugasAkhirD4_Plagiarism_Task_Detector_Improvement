from src.utils.text_tokenize import tokenize_word, tokenize_sentence, tokenize_character

def test_tokenize_word():
    text = "Indonesia adalah negara yang besar."
    result = tokenize_word(text)
    assert result == ['Indonesia', 'adalah', 'negara', 'yang', 'besar', '.']

def test_tokenize_sentence():
    text = "Presiden datang. Prof. Budi menyambut."
    result = tokenize_sentence(text)
    assert result == ['Presiden datang.', 'Prof. Budi menyambut.']

def test_tokenize_charachter():
    word_tokens = ['Indonesia', 'adalah', ' ', '.']
    result = tokenize_character(word_tokens)
    assert result == ['I', 'n', 'd', 'o', 'n', 'e', 's', 'i', 'a', 'a', 'd', 'a', 'l', 'a', 'h', ' ', '.']