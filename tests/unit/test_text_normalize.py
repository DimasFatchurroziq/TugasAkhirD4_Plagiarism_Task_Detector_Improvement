from src.infrastructures.preprocessing.text_normalize import remove_special_character

def test_remove_special_character_basic():
    text = "AI Generator!!!"
    assert remove_special_character(text) == "AI Generator"

def test_remove_special_character_mixed():
    text = "AI@2024#Generator$%^"
    assert remove_special_character(text) == "AI2024Generator"

def test_remove_special_character_with_spaces():
    text = "Hello,   World!!!"
    assert remove_special_character(text) == "Hello   World"

def test_remove_special_character_newline_tab():
    text = "Hello\nWorld\tAI!!!"
    assert remove_special_character(text) == "Hello\nWorld\tAI"

def test_remove_special_character_only_special():
    text = "!@#$%^&*()_+=-"
    assert remove_special_character(text) == ""

def test_remove_special_character_long_text():
    text = (
        "Artificial Intelligence (AI)!!! is changing the world—fast. "
        "In 2024, companies use AI for data-analysis, automation & decision-making."
    )

    expected = (
        "Artificial Intelligence AI is changing the worldfast "
        "In 2024 companies use AI for dataanalysis automation  decisionmaking"
    )

    assert remove_special_character(text) == expected
