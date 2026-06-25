"""
PDF Block Segmentation & Classifier
=====================================
Dua jalur klasifikasi:

  1. DIGITAL TEXT (PyMuPDF)
     -> BlockType.TEXT  |  BlockType.CODE

  2. IMAGE / SCAN (OCR via Tesseract)
     -> BlockType.CODE  |  BlockType.TERMINAL_OUTPUT

Digunakan sebagai preprocessing sebelum engine deteksi plagiarisme.
"""

import fitz
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound


# ══════════════════════════════════════════════════════════
# Enum & Dataclass
# ══════════════════════════════════════════════════════════

class BlockType(str, Enum):
    TEXT            = "TEXT"
    CODE            = "CODE"
    TERMINAL_OUTPUT = "TERMINAL_OUTPUT"


class SourceType(str, Enum):
    DIGITAL = "DIGITAL"
    OCR     = "OCR"


@dataclass
class TextBlock:
    page_num    : int
    block_index : int
    raw_text    : str
    block_type  : BlockType
    source_type : SourceType
    font_names  : list = field(default_factory=list)
    confidence  : float = 1.0
    language    : Optional[str] = None


# ══════════════════════════════════════════════════════════
# Konstanta — Font
# ══════════════════════════════════════════════════════════

MONOSPACE_FONTS = {
    "courier", "consolas", "monaco", "menlo", "lucidaconsole",
    "sourcecodepro", "dejavusansmono", "inconsolata", "robotomono",
    "ubuntumono", "nimbusmonol", "freemono", "droidsansmono",
    "anonymouspro", "couriernew", "terminal", "fixedsys",
}


# ══════════════════════════════════════════════════════════
# Konstanta — Keyword Kode (Dua Bobot)
# ══════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════
# Konstanta — Pola Terminal
# ══════════════════════════════════════════════════════════

TERMINAL_PATTERNS = [
    # Shell / Prompt
    r"^\$\s+\S",
    r"^>>>\s",
    r"^C:\\.*>",
    r"^root@",
    r"^\w+@[\w\-]+",

    # Error & Exception
    r"^Traceback \(most",
    r"^\s+at\s+\w+\(",
    r"^Exception in ",
    r"^Error:",
    r"^.*Error:.*line\s+\d+",

    # Log Format
    r"^\[.*\]\s+INFO",
    r"^\[.*\]\s+ERROR",
    r"^\[.*\]\s+DEBUG",
    r"^\[.*\]\s+WARNING",

    # Build / IDE Output
    r"^Process finished",
    r"^BUILD (SUCCESS|FAILED)",

    # Path Windows
    r"^[A-Z]:\\",
    r"^[A-Z]:\\.*?>",

    # Output Program Interaktif — Bahasa Indonesia
    r"^Pilih(an)?[\s:]",
    r"^\d+\.\s+[A-Z][a-z]+\s+[A-Z]",
    r"^Masukkan\s+\w+",
    r"^Data\s+(ditemukan|tidak\s+ditemukan|pegawai|awal|akhir)",
    r"^Tambahkan\s+data",
    r"^Sebelum\s+atau\s+sesudah",
    r"^Hasil\s+(pencarian|pengurutan|eksekusi)",
    r"^Tidak\s+ditemukan",
    r"^Ditemukan\s+pada",

    # Output Data Terstruktur
    r"^(NIP|Nama|Alamat|Golongan|ID|Kode|Harga|Stok)\s*:\s*\S",
    r"^NIP\s*:\s*\d+.*Nama\s*:",
]
TERMINAL_RE = [re.compile(p, re.MULTILINE) for p in TERMINAL_PATTERNS]


# ══════════════════════════════════════════════════════════
# Helper
# ══════════════════════════════════════════════════════════

def _is_monospace(font_names):
    for fn in font_names:
        normalized = fn.lower().replace(" ", "").replace("-", "")
        for mono in MONOSPACE_FONTS:
            if mono in normalized:
                return True
    return False


def _has_code_keywords(text):
    return any(kw in text for kw in CODE_KEYWORDS)


def _count_strong_keywords(text):
    """Hitung jumlah keyword kuat yang ditemukan dalam teks."""
    return sum(1 for kw in CODE_KEYWORDS_STRONG if kw in text)


def _count_weak_keywords(text):
    """Hitung jumlah keyword lemah yang ditemukan dalam teks."""
    return sum(1 for kw in CODE_KEYWORDS_WEAK if kw in text)


def _count_structure_signals(text):
    """Hitung berapa pola struktur kode yang cocok."""
    return sum(1 for p in CODE_STRUCTURE_RE if p.search(text))


def _has_terminal_pattern(text):
    return any(p.search(text) for p in TERMINAL_RE)


def _detect_language_pygments(text):
    try:
        lexer = guess_lexer(text)
        name = lexer.name
        return None if name.lower() in ("text only", "plaintext") else name
    except ClassNotFound:
        return None


def _special_char_ratio(text):
    if not text:
        return 0.0
    specials = sum(1 for c in text if c in "{}[]();:=<>!&|/\\@#")
    return specials / len(text)


# ══════════════════════════════════════════════════════════
# Classifier: JALUR 1 — Digital Text
# Output: TEXT | CODE
# ══════════════════════════════════════════════════════════

def classify_digital_block(text, font_names):
    """
    Klasifikasi blok teks digital dari PyMuPDF.
    Hanya menghasilkan: TEXT atau CODE.

    Dua jalur berdasarkan kehadiran font monospace:

    A) Font Monospace:
       Sinyal layout sudah kuat, cukup satu konfirmasi konten.

    B) Font Bukan Monospace (kode di-paste dengan font biasa):
       Gunakan akumulasi sinyal berbobot. Butuh skor >= 3.

       Tabel bobot:
         +2  keyword KUAT pertama ditemukan  (def, class, #include, ...)
         +1  keyword KUAT ke-2 dst           (maks total dari kuat = 3)
         +1  keyword LEMAH ditemukan         (return, import, ...)
         +1  sym_ratio > 0.08
         +1  >= 2 pola struktur kode         (indentasi, }, ;, //, ...)
         +1  Pygments mendeteksi bahasa
    """
    text = text.strip()
    if not text:
        return BlockType.TEXT, 1.0, None

    is_mono   = _is_monospace(font_names)
    sym_ratio = _special_char_ratio(text)

    # ── Jalur A: Font Monospace ───────────────────────────────────────
    # Font adalah sinyal layout yang reliable. Satu konfirmasi cukup.
    if is_mono:
        has_any_kw = (_count_strong_keywords(text) + _count_weak_keywords(text)) > 0
        if has_any_kw:
            lang = _detect_language_pygments(text)
            return BlockType.CODE, 0.95, lang
        if sym_ratio > 0.04:
            lang = _detect_language_pygments(text)
            return BlockType.CODE, 0.85, lang
        lang = _detect_language_pygments(text)
        return BlockType.CODE, (0.80 if lang else 0.65), lang

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
        return BlockType.CODE, confidence, lang

    return BlockType.TEXT, 0.95, None


# ══════════════════════════════════════════════════════════
# Classifier: JALUR 2 — OCR dari Gambar
# Output: CODE | TERMINAL_OUTPUT
# ══════════════════════════════════════════════════════════

def classify_ocr_block(text):
    """
    Klasifikasi teks hasil OCR dari gambar dalam PDF.
    Hanya menghasilkan: CODE atau TERMINAL_OUTPUT.

    Kode program jarang muncul di terminal (kecuali REPL),
    sehingga threshold untuk CODE sengaja ditinggikan:
    butuh minimal 2 sinyal kuat agar diklasifikasi CODE.
    """
    text = text.strip()
    if not text:
        return BlockType.TERMINAL_OUTPUT, 0.5, None

    # Layer 1: Terminal — pola sangat spesifik
    if _has_terminal_pattern(text):
        return BlockType.TERMINAL_OUTPUT, 0.92, None

    # Layer 2: Akumulasi sinyal CODE (min. 2)
    signals = 0
    lang    = None

    if _has_code_keywords(text):
        signals += 1

    if _special_char_ratio(text) > 0.08:
        signals += 1

    detected_lang = _detect_language_pygments(text)
    if detected_lang:
        signals += 1
        lang = detected_lang

    if signals >= 2:
        return BlockType.CODE, round(0.70 + signals * 0.05, 2), lang

    return BlockType.TERMINAL_OUTPUT, 0.60, None


# ══════════════════════════════════════════════════════════
# OCR untuk Blok Gambar
# ══════════════════════════════════════════════════════════

def _run_ocr_on_images(page, page_num):
    results = []
    try:
        from PIL import Image
        import pytesseract
        import io
    except ImportError:
        return results

    for img_idx, img_info in enumerate(page.get_images(full=True)):
        xref = img_info[0]
        try:
            base_image = page.parent.extract_image(xref)
            image      = Image.open(io.BytesIO(base_image["image"]))
            ocr_text   = pytesseract.image_to_string(
                image, config="--psm 6 --oem 3"
            ).strip()
            if not ocr_text:
                continue
            block_type, confidence, language = classify_ocr_block(ocr_text)
            results.append(TextBlock(
                page_num    = page_num,
                block_index = img_idx,
                raw_text    = ocr_text,
                block_type  = block_type,
                source_type = SourceType.OCR,
                font_names  = [],
                confidence  = confidence,
                language    = language,
            ))
        except Exception:
            continue
    return results


# ══════════════════════════════════════════════════════════
# Main Extractor
# ══════════════════════════════════════════════════════════

def extract_and_classify(pdf_path, run_ocr=True):
    """
    Ekstrak semua blok dari PDF dan klasifikasikan per jalur.

    Jalur DIGITAL -> classify_digital_block() -> TEXT | CODE
    Jalur OCR     -> classify_ocr_block()     -> CODE | TERMINAL
    """
    doc     = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc, start=1):

        # Jalur 1: Teks Digital
        raw_blocks = page.get_text("dict")["blocks"]
        extracted  = []

        for block_idx, block in enumerate(raw_blocks):
            if block.get("type") != 0:
                continue
            lines_text, font_names = [], []
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    t = span.get("text", "").strip()
                    if t:
                        lines_text.append(span["text"])
                    f = span.get("font", "")
                    if f and f not in font_names:
                        font_names.append(f)
            full_text = "\n".join(lines_text).strip()
            if full_text:
                extracted.append((full_text, font_names, block_idx))

        # Merge blok pendek berdekatan dengan font sama
        merged, i = [], 0
        while i < len(extracted):
            text, fonts, bidx = extracted[i]
            if (len(text) < 60
                    and i + 1 < len(extracted)
                    and set(fonts) == set(extracted[i + 1][1])):
                next_text, _, _ = extracted[i + 1]
                merged.append((text + "\n" + next_text, fonts, bidx))
                i += 2
            else:
                merged.append((text, fonts, bidx))
                i += 1

        for full_text, font_names, orig_idx in merged:
            block_type, confidence, language = classify_digital_block(
                full_text, font_names
            )
            results.append(TextBlock(
                page_num    = page_num,
                block_index = orig_idx,
                raw_text    = full_text,
                block_type  = block_type,
                source_type = SourceType.DIGITAL,
                font_names  = font_names,
                confidence  = confidence,
                language    = language,
            ))

        # Jalur 2: Gambar -> OCR
        if run_ocr:
            results.extend(_run_ocr_on_images(page, page_num))

    doc.close()
    return results


# ══════════════════════════════════════════════════════════
# Aggregator & Utility
# ══════════════════════════════════════════════════════════

def get_segments_by_type(blocks):
    segments = {
        BlockType.TEXT.value            : [],
        BlockType.CODE.value            : [],
        BlockType.TERMINAL_OUTPUT.value : [],
    }
    for blk in blocks:
        segments[blk.block_type.value].append(blk)
    return segments


def get_text_for_plagiarism(blocks, block_type):
    filtered = [b.raw_text for b in blocks if b.block_type == block_type]
    return "\n\n---BLOCK_SEPARATOR---\n\n".join(filtered)


# ══════════════════════════════════════════════════════════
# Report / Debug
# ══════════════════════════════════════════════════════════

def print_classification_report(blocks, show_text=False):
    digital = [b for b in blocks if b.source_type == SourceType.DIGITAL]
    ocr     = [b for b in blocks if b.source_type == SourceType.OCR]
    by_type = {t: 0 for t in BlockType}
    for b in blocks:
        by_type[b.block_type] += 1

    print("=" * 65)
    print("  LAPORAN KLASIFIKASI BLOK PDF")
    print("=" * 65)
    print("  Total blok            :", len(blocks))
    print("  |- Digital (PyMuPDF)  :", len(digital), " ->  TEXT | CODE")
    print("  '- OCR (Gambar)       :", len(ocr),     " ->  CODE | TERMINAL")
    print()
    print("  Hasil klasifikasi:")
    print("  |- TEXT               :", by_type[BlockType.TEXT])
    print("  |- CODE               :", by_type[BlockType.CODE])
    print("  '- TERMINAL_OUTPUT    :", by_type[BlockType.TERMINAL_OUTPUT])
    print("=" * 65)

    if show_text:
        print("\nDETAIL TIAP BLOK:\n")
        for blk in blocks:
            lang_info = (" [" + blk.language + "]") if blk.language else ""
            src_tag   = "[DIGITAL]" if blk.source_type == SourceType.DIGITAL else "[OCR]"
            conf_pct  = str(int(blk.confidence * 100)) + "%"
            print("  " + src_tag + " Hal." + str(blk.page_num) +
                  " Blok#" + str(blk.block_index) +
                  "  " + blk.block_type.value + lang_info +
                  "  conf=" + conf_pct)
            if blk.font_names:
                print("  Font  : " + ", ".join(blk.font_names))
            preview = blk.raw_text[:120].replace("\n", " ")
            ellipsis = "..." if len(blk.raw_text) > 120 else ""
            print("  Teks  : " + preview + ellipsis)
            print()