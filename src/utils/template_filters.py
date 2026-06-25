"""
app/utils/template_filters.py
Custom Jinja2 filters & global functions.
"""

from fastapi.templating import Jinja2Templates
from datetime import datetime

import os
import hashlib
from functools import lru_cache


def register_filters(templates: Jinja2Templates) -> None:
    """Daftarkan semua custom filter ke instance Jinja2Templates."""
    print("REGISTER FILTER DIPANGGIL")
    env = templates.env

    # ── Filters ───────────────────────────────────────────────────

    def sim_class(value: int, threshold: int = 70) -> str:
        """Return CSS class berdasarkan persentase kemiripan."""
        if value >= threshold:
            return "high"
        elif value >= 40:
            return "med"
        return "low"

    def sim_stat_class(status: str) -> str:
        mapping = {
            "high":"red",
            "med": "amber",
            "low": "green",
        }
        return mapping.get(status, "")

    def progress_color(status: str) -> str:
        status = status.lower().strip()

        mapping = {
            "running":  "amber",
            "error":    "red",
        }
        return mapping.get(status, "")

    def sim_label(value: int, threshold: int = 70) -> str:
        if value >= threshold:
            return "Sangat Tinggi"
        elif value >= 40:
            return "Perlu Dicek"
        return "Aman"

    def status_label(status: str) -> str:
        status = status.lower().strip()

        mapping = {
            "pending":"Draf",
            "queue": "Antrian",
            "running": "Berjalan",
            "completed": "Selesai",
            "modified": "Dimodifikasi",
            "uploaded":"Diunggah",
            "processing": "Diproses",
            "done": "Selesai",
            "error": "Error",
        }
        return mapping.get(status, "")

    def badge_class(status: str) -> str:
        status = status.lower().strip()

        mapping = {
            ("uploaded", "view"):       "badge-uploaded",
            ("done", "completed"):      "badge-done",
            ("running", "processing"):  "badge-run",
            ("queue", "pending", "modified"):"badge-queue",
            ("error",):                 "badge-error",
            ("high",):                  "badge-high",
            ("med",):                   "badge-med",
            ("low",):                   "badge-low",
            ("delete",):                "badge-delete",
        }

        for keys, value in mapping.items():
            if status in keys:
                return value

        return ""

    def file_icon(filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        icons = {
            "pdf":  "ti-file-type-pdf",
            "docx": "ti-file-type-doc",
            "txt":  "ti-file-text",
        }
        return icons.get(ext, "ti-file")

    def file_icon_class(filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        classes = {"pdf": "pdf", "docx": "docx", "txt": "txt"}
        return classes.get(ext, "")

    def status_icon(status: str) -> str:
        status = status.lower().strip()

        mapping = {
            "pending":      "ti-notes",
            "modified":     "ti-adjustments-bolt",
            "completed":    "ti-check",
            "running":      "ti-loader-2",
            "queue":        "ti-clock",
            "error":        "ti-alert-circle",
        }
        return mapping.get(status, "")

    def zeropad(value: int, width: int = 2) -> str:
        return str(value).zfill(width)
    
    def time_ago(value):
        if isinstance(value, str):
            value = datetime.strptime(value.split('.')[0], "%Y-%m-%d %H:%M:%S")

        now = datetime.now()
        diff = now - value
        seconds = int(diff.total_seconds())

        if seconds < 60:
            return f"{seconds} detik lalu"
        elif seconds < 3600:
            return f"{seconds // 60} menit lalu"
        elif seconds < 86400:
            return f"{seconds // 3600} jam lalu"
        else:
            return f"{seconds // 86400} hari lalu"

    # --------------------------
    # Cache Busting Filter
    # --------------------------
    file_hash_cache = {}
    file_mtime_cache = {}



    # Cache ini akan otomatis terisi kembali dengan cepat saat server restart
    @lru_cache(maxsize=128)
    def dapatkan_hash_file(filepath: str, mtime: float) -> str:
        try:
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()[:8]
        except Exception:
            return "00000000"

    def cache_bust(filename: str) -> str:
        # Menggunakan path absolut agar aman dari mana pun server di-reload
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepah = os.path.join(base_dir, "src", "static", filename)

        filepath = os.path.join("src/static", filename)

        print(filepath)

        if not os.path.exists(filepath):
            # Tetap kembalikan jalur yang dipahami browser (/static/...)
            print(1)
            return f"/static/{filename}?v=00000000"

        # Ambil mtime dari file fisik
        mtime = os.path.getmtime(filepath)
        
        # Hitung hash
        hash_val = dapatkan_hash_file(filepath, mtime)

        return f"/static/{filename}?v={hash_val}"

    env.filters["sim_class"]       = sim_class
    env.filters["sim_stat_class"]  = sim_stat_class
    env.filters["progress_color"]  = progress_color
    env.filters["sim_label"]       = sim_label
    env.filters["status_label"]    = status_label
    env.filters["badge_class"]     = badge_class
    env.filters["file_icon"]       = file_icon
    env.filters["file_icon_class"] = file_icon_class
    env.filters["status_icon"]     = status_icon
    env.filters["zeropad"]         = zeropad
    env.filters['time_ago']        = time_ago
    env.filters["cache_bust"] = cache_bust


# --------------------------
# Cache Busting Filter
# --------------------------
file_hash_cache = {}
file_mtime_cache = {}

def cache_bust(filename: str) -> str:
    """
    Tambahkan query string hash ke URL file statis.
    Otomatis update jika file berubah.
    """
    filepath = os.path.join("static", filename)

    if not os.path.exists(filepath):
        return f"/static/{filename}?v=00000000"

    # Cek modified time
    mtime = os.path.getmtime(filepath)
    old_mtime = file_mtime_cache.get(filename)
    
    if old_mtime != mtime:
        # File baru atau berubah → hitung hash lagi
        with open(filepath, "rb") as f:
            file_hash_cache[filename] = hashlib.md5(f.read()).hexdigest()[:8]
        file_mtime_cache[filename] = mtime

    hash = file_hash_cache.get(filename, "00000000")
    return f"/static/{filename}?v={hash}"

# Daftarkan filter
