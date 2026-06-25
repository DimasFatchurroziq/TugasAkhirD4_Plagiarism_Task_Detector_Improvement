"""
app/services/job_service.py
Lapisan service — semua logika bisnis & data access.
Ganti bagian ini dengan database (SQLAlchemy / Tortoise ORM) sesuai kebutuhan.
"""

from typing import Optional
# from app.models.job import Job, FilePair, JobStatus, SimilarityLevel
from src.services import job_service, comparison_service

# ── Stats ─────────────────────────────────────────────────────────



# ── Pairs ─────────────────────────────────────────────────────────

def get_pairs(filter_level: Optional[str] = None):
    if filter_level and filter_level != "all":
        return [p for p in _PAIRS if p.status.value == filter_level]
    return _PAIRS


def get_pair(pair_id: int):
    return next((p for p in _PAIRS if p.id == pair_id), None)
