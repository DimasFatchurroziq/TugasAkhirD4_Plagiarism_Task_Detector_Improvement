# ================================================================
# Dockerfile — satu file untuk development dan production
# ================================================================

# ── Stage 1: Builder ──────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# Download model S-BERT sekali saat build, simpan ke /model-cache
# PYTHONPATH=/install/lib/... agar Python bisa temukan packages yang baru di-install
RUN PYTHONPATH=/install/lib/python3.11/site-packages python -c "\
from sentence_transformers import SentenceTransformer; \
model = SentenceTransformer('firqaaa/indo-sentence-bert-base'); \
model.save('/model-cache/indo-sentence-bert-base'); \
print('Model tersimpan.')"


# ── Stage 2: Runtime ──────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Tesseract OCR + OpenCV dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-ind tesseract-ocr-eng \
    libpq-dev libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Salin packages Python dari builder
COPY --from=builder /install /usr/local

# Salin model S-BERT dari builder
COPY --from=builder /model-cache /model-cache

# Salin kode — di development ini di-override oleh volume mount
# Di production, inilah kode yang dipakai
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini

RUN mkdir -p /app/uploads

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/src \
    SBERT_MODEL_PATH=/model-cache/indo-sentence-bert-base

EXPOSE 8000

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
