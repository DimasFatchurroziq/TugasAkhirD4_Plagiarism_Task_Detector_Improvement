.PHONY: help dev prod down logs shell db-shell migrate

help:
	@echo ""
	@echo "  DEV  (Anda)   : make dev"
	@echo "  PROD (Dosen)  : make prod"
	@echo "  Stop          : make down"
	@echo "  Log           : make logs"
	@echo "  Shell app     : make shell"
	@echo "  Shell DB      : make db-shell"
	@echo "  Migration baru: make migrate MSG='nama_migration'"
	@echo ""

dev:
	docker compose up --build
	
prod:
	docker compose -f docker-compose.prod.yml up --build

down:
	docker compose down
	docker compose -f docker-compose.prod.yml down 2>/dev/null || true

logs:
	docker compose logs -f app

shell:
	docker compose exec app bash

db-shell:
	docker compose exec db psql -U $${DB_USER:-plagiarism_user} -d $${DB_NAME:-plagiarism_db}

migrate:
	docker compose exec app alembic revision --autogenerate -m "$(MSG)"
	docker compose exec app alembic upgrade head
