# Makefile for Aura Art Django Application

.PHONY: help install dev test build docs clean docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	uv sync

dev: ## Start development server
	python manage.py runserver

test: ## Run tests
	python manage.py test

build: ## Build static files
	python manage.py collectstatic --noinput

docs: ## Build documentation
	cd docs && make html

clean: ## Clean build artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf docs/build/

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-shell: ## Open shell in web container
	docker-compose exec web bash

migrate: ## Run database migrations
	python manage.py migrate

migrate-docker: ## Run database migrations in Docker
	docker-compose exec web python manage.py migrate

superuser: ## Create superuser
	python manage.py createsuperuser

superuser-docker: ## Create superuser in Docker
	docker-compose exec web python manage.py createsuperuser

loaddata: ## Load initial data
	python manage.py loaddata setup/fill_up/artists.json
	python manage.py loaddata setup/fill_up/fake_artworks.json

loaddata-docker: ## Load initial data in Docker
	docker-compose exec web python manage.py loaddata setup/fill_up/artists.json
	docker-compose exec web python manage.py loaddata setup/fill_up/fake_artworks.json

deploy: ## Deploy to production
	./deploy.sh

check: ## Run Django system checks
	python manage.py check

format: ## Format code with black
	black .

lint: ## Run linting
	flake8 .

type-check: ## Run type checking
	mypy .
