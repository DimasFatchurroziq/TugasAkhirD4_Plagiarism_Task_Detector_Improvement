#!/bin/bash
set -e

echo "Menunggu PostgreSQL siap..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(os.environ['DATABASE_URL'].replace('+asyncpg',''))
except Exception as e:
    print(e); sys.exit(1)
"; do
    sleep 2
done
echo "PostgreSQL siap."

echo "Menjalankan migration..."
alembic upgrade head

# MODE=dev  → uvicorn dengan --reload (kode dibaca dari volume mount)
# MODE=prod → uvicorn tanpa --reload  (kode dari image)
if [ "$APP_MODE" = "dev" ]; then
    echo "Mode: DEVELOPMENT (live reload aktif)"
    exec uvicorn src.api.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
else
    echo "Mode: PRODUCTION"
    exec uvicorn src.api.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 2
fi
