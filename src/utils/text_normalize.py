import re

def remove_special_character(text: str) -> str:
    clean_text = re.sub(r'[^a-z0-9\s]', '', text).strip()
    return clean_text

# def normalize_source_code(code):
#     clean_code = 