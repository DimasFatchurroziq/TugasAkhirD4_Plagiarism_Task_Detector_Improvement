from src.utils.case_transform import change_to_lowercase, change_to_uppercase

def test_change_to_lowercase():
    text = "AI GeNERAToR 123 !?"
    result = change_to_lowercase(text)
    assert result == "ai generator 123 !?"

def test_change_to_uppercase():
    text = "ai GeneraTor 123 !?"
    result = change_to_uppercase(text)
    assert result == "AI GENERATOR 123 !?"