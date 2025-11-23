import re

def remove_special_charachter(text: str) -> str:
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return clean_text

# def normalize_source_code(code):
#     clean_code = 