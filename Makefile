.PHONY: setup run stop test lint smoke clean logs db-shell redis-shell migrate seed help

# Docker compose command (use 'docker compose' for newer Docker versions)
DOCKER_COMPOSE := docker compose

# Default target
help:
	@echo "StakeholderSim - Development Commands"
	@echo ""
	@echo "Setup & Run:"
	@echo "  make setup      - Install all dependencies and initialize database"
	@echo "  make run        - Start all services ($(DOCKER_COMPOSE) up)"
	@echo "  make stop       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo ""
	@echo "Development:"
	@echo "  make logs       - View logs from all services"
	@echo "  make backend    - Start only backend service"
	@echo "  make frontend   - Start only frontend service"
	@echo ""
	@echo "Database:"
	@echo "  make migrate    - Run database migrations"
	@echo "  make seed       - Seed database with test data"
	@echo "  make db-shell   - Open PostgreSQL shell"
	@echo "  make redis-shell - Open Redis CLI"
	@echo ""
	@echo "Testing:"
	@echo "  make test       - Run all tests"
	@echo "  make test-backend - Run backend tests"
	@echo "  make test-frontend - Run frontend tests"
	@echo "  make lint       - Run linters"
	@echo "  make smoke      - Run smoke tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Remove containers and volumes"

# Setup
setup:
	@echo "Setting up StakeholderSim..."
	cp -n .env.example .env 2>/dev/null || true
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up -d db redis
	@echo "Waiting for database..."
	sleep 5
	$(MAKE) migrate
	$(MAKE) seed
	@echo "Setup complete! Run 'make run' to start."

# Run services
run:
	$(DOCKER_COMPOSE) up

run-detached:
	$(DOCKER_COMPOSE) up -d

stop:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) restart

# Individual services
backend:
	$(DOCKER_COMPOSE) up backend

frontend:
	$(DOCKER_COMPOSE) up frontend

# Logs
logs:
	$(DOCKER_COMPOSE) logs -f

logs-backend:
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend:
	$(DOCKER_COMPOSE) logs -f frontend

# Database operations
migrate:
	$(DOCKER_COMPOSE) exec backend alembic upgrade head

migrate-create:
	@read -p "Migration name: " name; \
	$(DOCKER_COMPOSE) exec backend alembic revision --autogenerate -m "$$name"

seed:
	$(DOCKER_COMPOSE) exec backend python -m app.scripts.seed

db-shell:
	$(DOCKER_COMPOSE) exec db psql -U stakeholder_sim -d stakeholder_sim

redis-shell:
	$(DOCKER_COMPOSE) exec redis redis-cli

# Testing
test: test-backend test-frontend

test-backend:
	$(DOCKER_COMPOSE) exec backend pytest -v

test-frontend:
	$(DOCKER_COMPOSE) exec frontend npm test

lint:
	$(DOCKER_COMPOSE) exec backend ruff check app/
	$(DOCKER_COMPOSE) exec backend ruff format --check app/
	$(DOCKER_COMPOSE) exec frontend npm run lint

lint-fix:
	$(DOCKER_COMPOSE) exec backend ruff check --fix app/
	$(DOCKER_COMPOSE) exec backend ruff format app/
	$(DOCKER_COMPOSE) exec frontend npm run lint:fix

smoke:
	./scripts/smoke.sh

# Cleanup
clean:
	$(DOCKER_COMPOSE) down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/.next frontend/node_modules
