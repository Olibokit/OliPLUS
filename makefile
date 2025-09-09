# 🛠️ INSTALLATION

install-core:
    poetry install --extras "core"

install-full:
    poetry install --with dev --extras "core,ui,nlp,ocr,cli,networking,security,monitoring,workers,data"

install-dev:
    poetry install --with dev

install-ui:
    poetry install --extras "ui"

install-nlp:
    poetry install --extras "nlp"

install-ocr:
    poetry install --extras "ocr"

install-all-extras:
    poetry install --extras "core,ui,nlp,ocr,cli,networking,security,monitoring,workers,data"

install-firestore:
    poetry install --extras "firestore"

install-security:
    poetry install --extras "security"

install-monitoring:
    poetry install --extras "monitoring"

install-workers:
    poetry install --extras "workers"

install-cli:
    poetry install --extras "cli"

install-data:
    poetry install --extras "data"

install-db-sync:
    poetry install --extras "db-sync"

install-db-async:
    poetry install --extras "db-async"

# 🚀 EXECUTION

run-backend:
    uvicorn backend.main:app --reload

run-dashboard-ui:
    python dashboard_ui.py

run-init-env:
    python init_env.py

run-cli:
    python cockpit_main.py

# 🧪 TESTS

test:
    pytest

test-cov:
    pytest --cov=backend --cov-report=term-missing

# 🧼 LINTING & FORMATAGE

lint:
    ruff check .
    black --check .
    isort --check-only .

format:
    black .
    isort .
    ruff check . --fix

# 🧹 CLEANUP

clean-pyc:
    find . -name "*.pyc" -delete

clean-cache:
    rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache

clean-all: clean-pyc clean-cache

# 🧪 TYPE CHECKING

type-check:
    mypy backend/

# 🧰 DEV SHORTCUTS

dev:
    make install-dev && make run-backend

dev-full:
    make install-full && make run-backend && make run-dashboard-ui

# 🧾 INFO

info:
    @echo "📦 OLIPLUS Project Makefile"
    @echo "Available commands:"
    @grep -E '^[a-zA-Z_-]+:' Makefile | cut -d ':' -f 1 | sort

cockpit:
    @echo "🛩️ Cockpit OLIPLUS — Commandes typées"
    @make info
    @echo "Modules installés : core, ui, nlp, ocr, cli, etc."
    @echo "Pour lancer le dashboard : make run-dashboard-ui"
