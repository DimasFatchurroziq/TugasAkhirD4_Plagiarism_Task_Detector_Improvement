def change_to_lowercase(text: str) -> str:
    lower_text = text.lower()
    return lower_text

def change_to_uppercase(text: str) -> str:
    upper_text = text.upper()
    return upper_text

if __name__ == "__main__":
    path_file = "Wrizzle’s AI Text Generator: This AI tool can create ideas, drafts, or complete text for various purposes, such as articles, social posts, and emails. It can help you generate content quickly and efficiently. These tools can help you create unique and visually appealing text for various applications."
    asu = change_to_lowercase(path_file)
    asi = change_to_uppercase(path_file)
    print(asu)
    print(asi)
