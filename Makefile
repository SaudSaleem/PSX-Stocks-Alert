.PHONY: help build up down restart logs shell db-shell migrate test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "Services started! API available at http://localhost:8000"
	@echo "API Docs available at http://localhost:8000/docs"

down: ## Stop all services
	docker-compose down

restart: ## Restart backend service
	docker-compose restart backend

logs: ## Show backend logs (follow mode)
	docker-compose logs -f backend

logs-all: ## Show all logs (follow mode)
	docker-compose logs -f

shell: ## Open shell in backend container
	docker-compose exec backend bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U stocksuser -d stocks_alert

migrate: ## Run database migrations
	docker-compose exec backend alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="your message")
	docker-compose exec backend alembic revision --autogenerate -m "$(MSG)"

test: ## Run tests (if you have tests)
	docker-compose exec backend pytest

clean: ## Stop services and remove volumes
	docker-compose down -v
	@echo "All services stopped and volumes removed"

dev: ## Start development environment
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then cp env.example .env; echo "Created .env file - please edit it with your credentials"; fi
	make build
	make up
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Checking backend status..."
	@docker-compose ps backend || true
	@echo "Development environment ready!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Note: Migrations run automatically on container startup"
	@echo "View logs with: make logs"

status: ## Check status of services
	docker-compose ps

health: ## Check health of backend service
	@curl -s http://localhost:8000/ | grep -q "Welcome" && echo "✅ Backend is healthy" || echo "❌ Backend is not responding"

