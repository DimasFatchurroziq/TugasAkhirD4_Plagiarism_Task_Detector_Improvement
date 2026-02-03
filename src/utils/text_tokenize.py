import spacy

nlp = spacy.blank("en")
nlp.add_pipe('sentencizer')

def tokenize_character(word_tokens):
    character_tokens = []
    for word in word_tokens:
        character_tokens.extend(list(word))
    return character_tokens

def tokenize_word(text):
    doc = nlp(text)
    word_tokens = [token.text for token in doc]
    return word_tokens

def tokenize_sentence(text):
    doc = nlp(text)
    sentence_tokens = [sent.text for sent in doc.sents]
    return sentence_tokens