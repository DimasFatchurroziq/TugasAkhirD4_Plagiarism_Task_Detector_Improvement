import re

def convert_pdf_font_to_css(raw_font_name):
    """
    Mengonversi nama font hasil ekstrak PDF (PostScript/Subset)
    menjadi properti font CSS (font-family, font-weight, font-style).
    """
    if not raw_font_name or not isinstance(raw_font_name, str):
        return "font-family: sans-serif;"

    # 1. Bersihkan Subset Font (Menghapus 'AAAAAA+' jika ada)
    # Contoh: 'KTLMNO+ArialMT' -> 'ArialMT'
    clean_name = re.sub(r'^[A-Z]{6}\+', '', raw_font_name)

    # Buat variabel untuk menampung properti CSS
    font_weight = "normal"
    font_style = "normal"

    # 2. Deteksi Bold & Italic dari nama font sebelum dibersihkan total
    clean_name_lower = clean_name.lower()

    if "bold" in clean_name_lower or "-bd" in clean_name_lower:
        font_weight = "bold"
    if "italic" in clean_name_lower or "ital" in clean_name_lower or "-it" in clean_name_lower or "oblique" in clean_name_lower:
        font_style = "italic"

    # 3. Bersihkan sufiks umum PostScript/Vendor agar tersisa nama dasarnya saja
    # Menghapus -Bold, -Italic, MT, PS, Regular, dll.
    clean_name = re.sub(r'[-_]?(bold|italic|ital|regular|ps|mt|bd|it|oblique)', '', clean_name, flags=re.IGNORECASE)

    # Trim spasi atau sisa karakter aneh di ujung
    clean_name = clean_name.strip("-_ ")

    # 4. Mapping Nama Dasar Font ke Font Family CSS Standard + Fallback
    font_map = {
        "arial": "'Arial', Helvetica, sans-serif",
        "timesnewroman": "'Times New Roman', Times, serif",
        "couriernew": "'Courier New', Courier, monospace",
        "helvetica": "'Helvetica', Arial, sans-serif",
        "georgia": "'Georgia', serif",
        "verdana": "'Verdana', Geneva, sans-serif",
        "trebuchet": "'Trebuchet MS', Helvetica, sans-serif",
        "calibri": "'Calibri', Candara, sans-serif",
        "cambria": "'Cambria', Georgia, serif"
    }

    # Cari nama dasar yang cocok di dalam map (case-insensitive)
    lookup_key = clean_name.lower().replace(" ", "") # Hapus spasi untuk pencocokan yang akurat
    # font_family = font_map.get(lookup_key, f'"{clean_name}", sans-serif') # jika tidak ada di map, gunakan nama aslinya
    font_family = font_map.get(lookup_key, f"'{clean_name}', sans-serif")

    # 5. Susun menjadi string CSS
    css_string = f"font-family: {font_family};"
    if font_weight != "normal":
        css_string += f" font-weight: {font_weight};"
    if font_style != "normal":
        css_string += f" font-style: {font_style};"

    return css_string

# ==========================================
# CONTOH PENGGUNAAN (TEST CASE)
# ==========================================
# test_fonts = [
#     "CourierNewPSMT",
#     "KTLMNO+Arial-BoldMT",
#     "TimesNewRomanPS-ItalicMT",
#     "AAAAAA+Helvetica",
#     "UnknownCustomFont-Bold"
# ]

# print("--- Hasil Konversi ke CSS ---")
# for pdf_font in test_fonts:
#     css_result = convert_pdf_font_to_css(pdf_font)
#     print(f"{pdf_font:<30} -> {css_result}")