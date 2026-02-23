from src.infrastructures.preprocessing.case_transform import change_to_lowercase, change_to_uppercase

#lower case
def test_change_to_lowercase_basic():
    text = "AI GeNERAToR 123 !?"
    assert change_to_lowercase(text) == "ai generator 123 !?"

def test_change_to_lowercase_empty_string():
    text = ""
    assert change_to_lowercase(text) == ""

def test_change_to_lowercase_only_numbers():
    text = "123456"
    assert change_to_lowercase(text) == "123456"

def test_change_to_lowercase_only_symbols():
    text = "!@#$%^&*()"
    assert change_to_lowercase(text) == "!@#$%^&*()"

def test_change_to_lowercase_with_spaces():
    text = "  HELLO   WORLD  "
    assert change_to_lowercase(text) == "  hello   world  "

def test_change_to_lowercase_newline_tab():
    text = "HELLO\nWORLD\tAI"
    assert change_to_lowercase(text) == "hello\nworld\tai"

def test_change_to_lowercase_long_text():
    text = (
        "Artificial Intelligence (AI) is Transforming the World in 2024. "
        "Many Companies Use AI FOR Data Analysis, Automation, and Decision Making. "
        "However, Not ALL Challenges Can Be Solved BY AI Alone!"
    )

    expected = (
        "artificial intelligence (ai) is transforming the world in 2024. "
        "many companies use ai for data analysis, automation, and decision making. "
        "however, not all challenges can be solved by ai alone!"
    )

    assert change_to_lowercase(text) == expected


#upper case
def test_change_to_uppercase_python_code():
    code = "def add(a, b):\n    return a + b"
    expected = "DEF ADD(A, B):\n    RETURN A + B"
    assert change_to_uppercase(code) == expected

def test_change_to_uppercase_js_code():
    code = "function sum(x, y) { return x + y; }"
    expected = "FUNCTION SUM(X, Y) { RETURN X + Y; }"
    assert change_to_uppercase(code) == expected

def test_change_to_uppercase_with_comments():
    code = "# This is a comment\nprint('hello world')"
    expected = "# THIS IS A COMMENT\nPRINT('HELLO WORLD')"
    assert change_to_uppercase(code) == expected

def test_change_to_uppercase_empty_string():
    code = ""
    expected = ""
    assert change_to_uppercase(code) == expected

def test_change_to_uppercase_numbers_and_symbols():
    code = "x = 10 + 20 * 3 / 2"
    expected = "X = 10 + 20 * 3 / 2"
    assert change_to_uppercase(code) == expected
