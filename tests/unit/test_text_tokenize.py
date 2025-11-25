from src.utils.text_tokenize import tokenize_word, tokenize_sentence

def test_tokenize_word():
    text = "Indonesia adalah negara yang besar."
    result = tokenize_word(text)
    assert result == ['Indonesia', 'adalah', 'negara', 'yang', 'besar', '.']

def test_tokenize_sentence():
    text = "Presiden datang. Prof. Budi menyambut."
    result = tokenize_sentence(text)
    assert result == ['Presiden datang.', 'Prof. Budi menyambut.']