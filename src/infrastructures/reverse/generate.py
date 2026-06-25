import re


bg_colors_text = [
    "#FFB3BA", "#FFC4E1", "#FFCCD5", "#FDE2E4", "#FFDFBA", "#FFDAC1", 
    "#FFD6A5", "#FFE5D9", "#FFFFBA", "#FFF1C5", "#FFF9A6", "#E2F0CB", 
    "#BAFFC9", "#99F3BD", "#CAFFBF"
]

bg_colors_code = [
    "#BFFCC6", "#E8FFC4", "#A8E6CF", 
    "#A2E8DD", "#C4FAF8", "#BAE1FF", "#D6E4FF", "#BDE0FE", "#A0C4FF", 
    "#DCF2F1", "#E8AEFF", "#DCD6F7", "#F4EEFF", "#E3DFFD", "#F3CCFF"
]



def generate_tuple_color(list_match_mapping):

    # print(list_match_mapping)

    target_ranges = {}

    for group in list_match_mapping:
        for item in group["block"]:
            start = item["start"]
            end = item["end"]
            idx_color = item["tile_source"]

            if item["type"] == "TEXT":            
                if idx_color is not None:
                    modulus = idx_color % 15
                    color = bg_colors_text[modulus]
                else:
                    color = "transparent"
            elif item["type"] == "CODE":
                if idx_color is not None:
                    modulus = idx_color % 15
                    color = bg_colors_code[modulus]
                else:
                    color = "transparent"

            target_ranges[(start, end)] = color
    # print(target_ranges)

    return target_ranges


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


def rgb_to_hex(color_int):
    """Convert PyMuPDF color int ke hex"""
    r = (color_int >> 16) & 255
    g = (color_int >> 8) & 255
    b = color_int & 255
    return f"#{r:02x}{g:02x}{b:02x}"


    
          