import pytesseract
import cv2
import numpy as np

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import os
tesseract_path = os.getenv("TESSERACT_CMD")
if tesseract_path:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


def ocr_code_image(image_bytes: bytes, lang: str = "eng") -> str:
    """
    OCR khusus gambar berisi kode program dengan perbaikan thresholding
    """
    # bytes → image
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image")

    # 1. Grayscale (Wajib)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Upscale (Perbesar 2x dengan INTER_CUBIC agar ujung huruf halus)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # 3. Gunakan OTSU Thresholding (Lebih bersahabat untuk teks digital dibanding Adaptive)
    # Ini akan membuat background murni putih dan teks murni hitam tanpa merusak huruf
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 4. OCR config: Gunakan PSM 4 atau 6
    # --psm 4 biasanya sangat baik untuk mempertahankan baris asli tanpa double newline
    config = r"--psm 4 -c preserve_interword_spaces=1"

    # Jalankan OCR menggunakan gambar 'thresh' yang sudah bersih
    text = pytesseract.image_to_string(thresh, lang=lang, config=config)

    # --- PROSES AKHIR: Pembersihan Selektif Fleksibel ---
    lines = text.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        # Jika baris saat ini kosong, cek baris sebelum dan sesudahnya
        if line.strip() == "":
            if i > 0 and i < len(lines) - 1:
                prev_line = lines[i-1].strip().lower()
                next_line = lines[i+1].strip().lower()
                
                # Cek apakah baris sebelum DAN sesudahnya sama-sama mengandung kata 'import'
                is_import_block = prev_line.startswith("import") or prev_line.startswith("from") and \
                                  next_line.startswith("import") or next_line.startswith("from")
                
                # Cek apakah baris sebelum DAN sesudahnya sama-sama mengandung kata 'self'
                is_self_block = prev_line.startswith("self") and next_line.startswith("self")
                
                # Jika terdeteksi di dalam blok yang harusnya rapat, hapus baris kosong ini
                if is_import_block or is_self_block:
                    continue
                    
        cleaned_lines.append(line)

    final_text = '\n'.join(cleaned_lines)
    return text