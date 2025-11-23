from src.utils.text_normalize import remove_special_charachter

def test_remove_special_charachter():
    text = "ai GeneraTor 123 !?"
    result = remove_special_charachter(text)
    assert result == "ai GeneraTor 123 "