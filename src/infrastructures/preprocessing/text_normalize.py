import re

def remove_special_character(text: str) -> str:
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text.strip()

# def remove_special_character(text: str) -> str:
#     clean_text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
#     clean_text = re.sub(r' +', ' ', clean_text)
#     return clean_text.strip()

# def normalize_source_code(code):
#     clean_code = 

def clean_pdf_text(text):
    replacements = {
        "\xa0": " ",
        "\u2002": " ",
        "\u2003": " ",
        "\u2009": " ",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\u00ad": "",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)
        
    return text