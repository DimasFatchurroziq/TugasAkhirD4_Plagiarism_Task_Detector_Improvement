import re

def remove_special_character(text: str) -> str:
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text.strip()

# def remove_special_character(text: str) -> str:
#     clean_text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
#     clean_text = re.sub(r' +', ' ', clean_text)
#     return clean_text.strip()

# def normalize_source_code(code):
#     clean_code = 