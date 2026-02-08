from src.utils.text_tokenize import tokenize_word, tokenize_sentence, tokenize_character

#Tokenisasi kalimat
def test_tokenize_sentence_basic():
    text = "Hello world. This is AI."
    expected = ["Hello world.", "This is AI."]
    assert tokenize_sentence(text) == expected

def test_tokenize_sentence_no_period():
    text = "Hello world"
    expected = ["Hello world"]
    assert tokenize_sentence(text) == expected

def test_tokenize_sentence_multiline():
    text = "Hello world.\nHow are you today? I hope all is well."
    expected = ["Hello world.", "\nHow are you today?", "I hope all is well."]
    assert tokenize_sentence(text) == expected

def test_tokenize_sentence_question_exclamation():
    text = "Wow! Is this real? Yes, it is."
    expected = ["Wow!", "Is this real?", "Yes, it is."]
    assert tokenize_sentence(text) == expected

def test_tokenize_sentence_long_text():
    text = (
        "Artificial Intelligence is transforming the world. "
        "Many companies use AI for data analysis, automation, and decision making. "
        "However, challenges remain!"
    )
    expected = [
        "Artificial Intelligence is transforming the world.",
        "Many companies use AI for data analysis, automation, and decision making.",
        "However, challenges remain!"
    ]
    assert tokenize_sentence(text) == expected


#tokenisalsi kata
def test_tokenize_word_basic():
    text = "Hello world!"
    expected = ["Hello", "world", "!"]
    assert tokenize_word(text) == expected

def test_tokenize_word_punctuation():
    text = "AI, data, and ML."
    expected = ["AI", ",", "data", ",", "and", "ML", "."]
    assert tokenize_word(text) == expected

def test_tokenize_word_multiline():
    text = "Hello world.\nHow are you?"
    expected = ["Hello", "world", ".", "\n", "How", "are", "you", "?"]
    assert tokenize_word(text) == expected

def test_tokenize_word_special_chars():
    text = "Wow! AI@2024 #ML"
    expected = ["Wow", "!", "AI@2024", "#", "ML"]
    assert tokenize_word(text) == expected

def test_tokenize_word_long_text():
    text = (
        "Artificial Intelligence is transforming the world. "
        "Many companies use AI for data analysis, automation, and decision making!"
    )
    expected = [
        "Artificial", "Intelligence", "is", "transforming", "the", "world", ".", 
        "Many", "companies", "use", "AI", "for", "data", "analysis", ",", 
        "automation", ",", "and", "decision", "making", "!"
    ]
    assert tokenize_word(text) == expected


#tokenisasi karakter
def test_tokenize_character_basic():
    words = ["Hello", "AI"]
    expected = ['H', 'e', 'l', 'l', 'o', 'A', 'I']
    assert tokenize_character(words) == expected

def test_tokenize_character_with_numbers():
    words = ["AI", "2024"]
    expected = ['A', 'I', '2', '0', '2', '4']
    assert tokenize_character(words) == expected

def test_tokenize_character_empty_list():
    words = []
    expected = []
    assert tokenize_character(words) == expected

def test_tokenize_character_single_character_words():
    words = ["A", "B", "C"]
    expected = ["A", "B", "C"]
    assert tokenize_character(words) == expected

def test_tokenize_character_long_word():
    words = ["Artificial"]
    expected = list("Artificial")  # ['A', 'r', 't', 'i', 'f', 'i', 'c', 'i', 'a', 'l']
    assert tokenize_character(words) == expected
