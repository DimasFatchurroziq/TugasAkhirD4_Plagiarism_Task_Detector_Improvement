from utils.case_transform import change_to_lowercase
from utils.text_normalize import remove_special_charachter
from utils.text_tokenize import tokenize_word, tokenize_sentence, tokenize_character

class PreprocessingService:
    def __init__(self, file_repository):
        self.file_repository = file_repository

    async def preprocessing_text(self, text) :
        lower_text = change_to_lowercase(text)
        clean_text = remove_special_charachter(lower_text)
        
        sentence_tokens = tokenize_sentence(clean_text)
        word_tokens = tokenize_word(clean_text)
        character_tokens = tokenize_character(word_tokens)
        
        # print(character_tokens)

        ############ ini nanti diubah ya, hehe
        # words = await self.hash_repository.create(word_tokens)
        # sentences = await self.hash_repository.create(sentence_tokens)

        return character_tokens
        