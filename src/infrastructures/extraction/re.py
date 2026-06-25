"""
PDF Block Segmentation & Classifier
====================================
Mengekstrak blok teks dari PDF dan mengklasifikasikan tiap blok
menjadi: CODE | TERMINAL_OUTPUT | TEXT

Digunakan sebagai preprocessing sebelum engine deteksi plagiarisme.
"""

import fitz  # PyMuPDF
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

from collections.abc import Iterable



# ──────────────────────────────────────────────
# Enum & Dataclass
# ──────────────────────────────────────────────

class BlockType(str, Enum):
    CODE            = "CODE"
    TERMINAL_OUTPUT = "TERMINAL_OUTPUT"
    TEXT            = "TEXT"


@dataclass
class TextBlock:
    page_num    : int
    block_index : int
    raw_text    : str
    block_type  : BlockType
    font_names  : list[str] = field(default_factory=list)
    confidence  : float = 1.0          # 0.0 – 1.0
    language    : Optional[str] = None  # bahasa pemrograman jika CODE


# ──────────────────────────────────────────────
# Konstanta
# ──────────────────────────────────────────────

MONOSPACE_FONTS = {
    "courier", "consolas", "consolasitalic", "monaco", "menlo", "lucidaconsole",
    "sourcecodepro", "dejavusansmono", "inconsolata", "robotomono",
    "ubuntumono", "nimbusmonol", "freemono", "droidsansmono",
    "anonymouspro", "courier new", "terminal", "fixedsys",
}

# ══════════════════════════════════════════════════════════
# Konstanta — Keyword Kode (Dua Bobot)
# ══════════════════════════════════════════════════════════
 
# Keyword KUAT: sangat spesifik untuk kode program,
# hampir tidak mungkin muncul di teks narasi biasa
CODE_KEYWORDS = {
    # =======================
    # Python
    # =======================
    "def ", "class ", "import ", "from ", "return ", "lambda ",
    "elif ", "yield ", "async ", "await ", "try:", "except ",
    "finally:", "with ", "as ", "pass", "break", "continue",
    "global ", "nonlocal ", "assert ", "del ",

    # =======================
    # Java / C / C++
    # =======================
    "public ", "private ", "protected ", "static ", "void ",
    "int ", "float ", "double ", "char ", "bool ",
    "#include", "namespace ", "using namespace",
    "template<", "typename ", "cout", "cin",
    "printf(", "scanf(", "#define",

    # =======================
    # JavaScript / TypeScript
    # =======================
    "function ", "const ", "let ", "var ", "=>",
    "async function", "await ",
    "interface ", "type ", "enum ",
    "export ", "import ", "require(",
    "console.log", "document.", "window.",

    # =======================
    # SQL
    # =======================
    "SELECT ", "INSERT ", "UPDATE ", "DELETE ",
    "CREATE TABLE", "DROP TABLE", "ALTER TABLE",
    "WHERE ", "JOIN ", "INNER JOIN", "LEFT JOIN",
    "GROUP BY", "ORDER BY", "HAVING ",
    "LIMIT ", "OFFSET ",

    # =======================
    # PHP
    # =======================
    "<?php", "echo ", "$", "->", "::",
    "function ", "namespace ", "use ",

    # =======================
    # Ruby
    # =======================
    "def ", "end", "puts ", "class ", "module ",
    "require ", "include ",

    # =======================
    # Go
    # =======================
    "func ", "package ", "import (", "defer ",
    "go ", "chan ", "select {",

    # =======================
    # HTML / XML
    # =======================
    "<html", "<div", "<span", "<head", "<body",
    "<script", "<style", "<!DOCTYPE",
    "</", "/>",

    # =======================
    # CSS
    # =======================
    # "{", "}", ":", ";",
    "margin", "padding", "color", "font-size",
    "display", "flex", "grid",

    # =======================
    # JSON / Data-like
    # =======================
    # "{", "}", "[", "]", "\"", ":", ",",

    # =======================
    # General programming patterns
    # =======================
    "if (", "else {", "for (", "while (",
    "switch (", "case ", "break;", "continue;",
    "try {", "catch (", "finally {",
    "==", "!=", "<=", ">=", "&&", "||",
    "++", "--", "+=", "-=", "*=", "/=", "//",
}

 
# ══════════════════════════════════════════════════════════
# Konstanta — Pola Terminal
# ══════════════════════════════════════════════════════════

TERMINAL_PATTERNS = [
    r"^\$\s+\S",          # $ command
    r"^>>>\s",            # Python REPL
    r"^C:\\.*>",          # Windows CMD
    r"^root@",            # Linux root prompt
    r"^\w+@[\w\-]+",


    # Error & Exception
    r"^Traceback \(most", # Python traceback
    r"^\s*at\s+\w+\(",    # Java stack trace
    r"^Exception in ",    # Java exception
    r"^Error:",           # Generic error
    r"^.*Error:.*line\s+\d+",

    # Log Format
    r"^\[.*\]\s+INFO",
    r"^\[.*\]\s+ERROR",
    r"^\[.*\]\s+DEBUG",
    r"^\[.*\]\s+WARNING",

    r"\.exe\b",                 # file executable Windows

    # Build / IDE Output
    r"process returned",        # output compiler/runtime
    r"execution time",          # info waktu eksekusi
    r"^Process finished",
    r"^BUILD (SUCCESS|FAILED)",
 
    # Path Windows
    r"^[A-Z]:\\",                         # D:\Muflih\Kuliah\...
    r"^[A-Z]:\\.*?>",                     # C:\Users\...>
]

TERMINAL_RE = [re.compile(p, re.MULTILINE  | re.IGNORECASE) for p in TERMINAL_PATTERNS]

###########################################################################################################################
# Keyword KUAT: sangat spesifik untuk kode program,
# hampir tidak mungkin muncul di teks narasi biasa
CODE_KEYWORDS_STRONG = {
    "def ",          # Python function
    "class ",        # OOP semua bahasa
    "#include",      # C/C++
    "public static", # Java
    "void ",         # Java/C
    "private ",      # OOP
    "protected ",    # OOP
    "namespace ",    # C++/PHP
    "template<",     # C++
    "<?php",         # PHP
    "func ",         # Go/Swift
    "SELECT ",       # SQL
    "INSERT INTO",   # SQL
    "CREATE TABLE",  # SQL
}

# Keyword LEMAH: bisa muncul di teks biasa
# Contoh: "return on investment", "import data dari Excel"
CODE_KEYWORDS_WEAK = {
    "return ", "import ", "from ", "lambda ",
    "elif ", "yield ", "async ", "await ",
    "static ", "function ", "const ", "let ",
    "var ", "=>", "interface ", "export ",
    "require(", "DELETE ", "UPDATE ", "package ",
}

# Untuk OCR dan helper lama — gabungan keduanya
CODE_KEYWORDS = CODE_KEYWORDS_STRONG | CODE_KEYWORDS_WEAK


# ══════════════════════════════════════════════════════════
# Konstanta — Pola Struktur Kode
# ══════════════════════════════════════════════════════════

# Pola yang mencerminkan struktur visual kode program
# (indentasi konsisten, blok kurung, komentar, dll.)
CODE_STRUCTURE_PATTERNS = [
    r"^    \S",                                       # indentasi 4 spasi
    r"^\t\S",                                         # indentasi tab
    r"^\s+(if|for|while|return|print|System)\b",      # baris indentasi + keyword
    r"\)\s*\{",                                       # penutup: ) {
    r"^\s*\}\s*$",                                    # baris penutup: }
    r";\s*$",                                         # akhir pernyataan: ;
    r"//.*$",                                         # komentar C-style: //
    r"^\s*#\s+\w+",                                   # komentar Python: # ...
    r"\.\w+\(",                                       # method call: obj.method(
]
CODE_STRUCTURE_RE = [re.compile(p, re.MULTILINE) for p in CODE_STRUCTURE_PATTERNS]
#######################################################################################################################

# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def _is_monospace(font_names: str | Iterable[str]) -> bool:
    # print(font_names)
    if isinstance(font_names, str):
        font_names = font_names.split(",")  # <-- FIX UTAMA
        # print("ya")

    # print("no")

    for fn in font_names:
        # print(fn)
        fn = fn.strip()
        normalized = fn.lower().replace(" ", "").replace("-", "")
        for mono in MONOSPACE_FONTS:
            if mono.replace(" ", "") in normalized:
                return True

    return False


def _has_code_keywords(text: str) -> bool:
    """Cek kehadiran keyword bahasa pemrograman."""
    for kw in CODE_KEYWORDS:
        if kw in text:
            return True
    return False


def _has_terminal_pattern(text: str) -> bool:
    """Cek apakah teks mirip output terminal."""
    for pattern in TERMINAL_RE:
        if pattern.search(text):
            return True
    return False


def _detect_language_pygments(text: str) -> Optional[str]:
    """Gunakan Pygments untuk mendeteksi bahasa pemrograman."""
    try:
        lexer = guess_lexer(text)
        name = lexer.name
        if name.lower() in ("text only", "plaintext"):
            return None
        return name
    except ClassNotFound:
        return None

##################################################################################33
def _count_special_chars_ratio(text: str) -> float:
    """Rasio karakter simbol kode terhadap total karakter."""
    if not text:
        return 0.0
    specials = sum(1 for c in text if c in "{}[]();:=<>!&|/\\@#")
    return specials / len(text)

def _count_strong_keywords(text):
    """Hitung jumlah keyword kuat yang ditemukan dalam teks."""
    return sum(1 for kw in CODE_KEYWORDS_STRONG if kw in text)


def _count_weak_keywords(text):
    """Hitung jumlah keyword lemah yang ditemukan dalam teks."""
    return sum(1 for kw in CODE_KEYWORDS_WEAK if kw in text)


def _count_structure_signals(text):
    """Hitung berapa pola struktur kode yang cocok."""
    return sum(1 for p in CODE_STRUCTURE_RE if p.search(text))


#####################################################################################33

def classify_list_content(data):
    # Ambil semua kategori unik yang ada di elemen pertama setiap item
    categories = {item[0] for item in data}
    
    # Logika penentuan kelas
    if "CODE" in categories and "TERMINAL" in categories:
        return "both_combined"
    elif "CODE" in categories:
        return "code_only"
    elif "TERMINAL" in categories:
        return "terminal_only"
    else:
        return "empty_or_unknown"

#####################################################################################



def classify_typing_true(text: str, font_names: str) -> tuple[BlockType, float, Optional[str]]:
    """
    Klasifikasi sebuah blok teks.

    Returns:
        (BlockType, confidence, language_name)
    """
    text_stripped = text.strip()
    if not text_stripped:
        return "TEXT", 1.0, None

    is_mono   = _is_monospace(font_names)
    has_kw    = _has_code_keywords(text_stripped)
    sym_ratio = _count_special_chars_ratio(text_stripped)

    if is_mono and has_kw:
        lang = _detect_language_pygments(text_stripped)
        return "CODE", 0.95, lang

    if is_mono and sym_ratio > 0.04:
        lang = _detect_language_pygments(text_stripped)
        return "CODE", 0.85, lang

    if is_mono:
        lang = _detect_language_pygments(text_stripped)
        return "CODE", (0.80 if lang else 0.65), lang

    if has_kw and sym_ratio > 0.07:
        lang = _detect_language_pygments(text_stripped)
        return "CODE", 0.75, lang

    return "TEXT", 0.95, None

def classify_typing_false(text: str, font_names: str) -> tuple[BlockType, float, Optional[str]]:
    """
    Klasifikasi sebuah blok teks.

    Returns:
        (BlockType, confidence, language_name)
    """
    text_stripped = text.strip()
    if not text_stripped:
        return "TEXT", 1.0, None

    is_mono   = _is_monospace(font_names)
    sym_ratio = _count_special_chars_ratio(text_stripped)

    if is_mono:
        has_any_kw = (_count_strong_keywords(text) + _count_weak_keywords(text)) > 0
        if has_any_kw:
            lang = _detect_language_pygments(text)
            return "CODE", 0.95, lang
        if sym_ratio > 0.04:
            lang = _detect_language_pygments(text)
            return "CODE", 0.85, lang
        lang = _detect_language_pygments(text)
        return "CODE", (0.80 if lang else 0.65), lang

    # ── Jalur B: Font Bukan Monospace ────────────────────────────────
    # Tanpa sinyal font, akumulasi minimal 3 sinyal konten diperlukan
    # agar tidak salah klasifikasi teks narasi yang kebetulan
    # menyebut keyword seperti "return" atau "import".
    score = 0
    lang  = None

    # Keyword kuat: +2 untuk pertama, +1 untuk setiap tambahan (maks 3)
    strong_count = _count_strong_keywords(text)
    if strong_count >= 1:
        score += 2
    if strong_count >= 2:
        score += min(strong_count - 1, 1)   # maks +1 tambahan

    # Keyword lemah: +1 jika ada
    if _count_weak_keywords(text) >= 1:
        score += 1

    # Rasio simbol: threshold lebih tinggi dari jalur A
    # karena tanda baca teks biasa (: , .) mudah menaikkan rasio
    if sym_ratio > 0.08:
        score += 1

    # Pola struktur kode: butuh minimal 2 pola cocok
    if _count_structure_signals(text) >= 2:
        score += 1

    # Pygments: konfirmasi akhir
    detected_lang = _detect_language_pygments(text)
    if detected_lang:
        score += 1
        lang = detected_lang

    if score >= 3:
        # Confidence proporsional dengan skor (rentang 0.69 - 0.92)
        confidence = round(min(0.65 + score * 0.04, 0.92), 2)
        return "CODE", confidence, lang

    return "TEXT", 0.95, None



def classify_image(text: str, font_names: str) -> tuple[BlockType, float, Optional[str]]:
    """
    Klasifikasi sebuah blok teks.

    Returns:
        (BlockType, confidence, language_name)
    """
    text_stripped = text.strip()
    if not text_stripped:
        return "TERMINAL", 0.5, None

    has_kw    = _has_code_keywords(text_stripped)
    has_term  = _has_terminal_pattern(text_stripped)
    sym_ratio = _count_special_chars_ratio(text_stripped)

    if has_term:
        return "TERMINAL", 0.92, None

    signals = 0
    lang    = None

    if has_kw:
        # lang = _detect_language_pygments(text_stripped)
        signals += 1
        # return "CODE", 0.88, lang

    if sym_ratio > 0.08:
        # lang = _detect_language_pygments(text_stripped)
        signals += 1
        # return "CODE", (0.80 if lang else 0.70), lang

    # if has_kw and sym_ratio > 0.08:
    #     lang = _detect_language_pygments(text_stripped)
    #     return "CODE", 0.75, lang

    lang = _detect_language_pygments(text_stripped)
    if lang:
        signals += 1
        # return "CODE", 0.75, lang
    # return "TERMINAL", 0.55, None


    if signals >= 2:
        return "CODE", round(0.70 + signals * 0.05, 2), lang
 
    # Layer 3: Default TERMINAL
    # Kode program murni tanpa sinyal apapun hampir tidak ada,
    # sedangkan output terminal tanpa keyword kode sangat umum
    return "TERMINAL", 0.60, None