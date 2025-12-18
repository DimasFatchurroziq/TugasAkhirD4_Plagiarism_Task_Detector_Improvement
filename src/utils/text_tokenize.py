import spacy

nlp = spacy.blank("en")

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
    nlp.add_pipe('sentencizer')
    doc = nlp(text)
    sentence_tokens = [sent.text for sent in doc.sents]
    return sentence_tokens