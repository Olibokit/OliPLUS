# 🛩️ OliPLUS — Cockpit d’automatisation / Automation Cockpit

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Poetry](https://img.shields.io/badge/poetry-managed-8A2BE2)
![License](https://img.shields.io/badge/license-MIT-green)
![Build](https://img.shields.io/github/actions/workflow/status/Olibokit/OliPLUS/ci.yml)

---

<details>
<summary>🇫🇷 Français</summary>

## ✨ Fonctionnalités principales
- 🔧 **API backend** avec FastAPI  
- 📊 **Dashboard interactif** avec Streamlit  
- 🧠 **NLP avancé** (Transformers, spaCy, NLTK)  
- 📄 **OCR et traitement PDF** (ocrmypdf, pytesseract)  
- 🔍 **Monitoring et observabilité** (Prometheus, Sentry, OpenTelemetry)  
- 🧬 **Pipelines de données** avec DuckDB et SQLModel  
- 🔐 **Authentification et sécurité renforcée**  
- 🧪 **Outils de dev intégrés** (tests, lint, type-check, pre-commit)  

---

## 🚀 Installation rapide
Installer tous les modules cockpitifiés :  
```bash
poetry install --extras "core full-backend full-ai full-dev"
Ou par domaine :

bash
poetry install --extras "nlp ocr ui dev"
📦 Modules cockpit
Groupe	Description	Commande
core	Backend minimal (FastAPI, uvicorn, loguru)	poetry install --extras "core"
full-backend	API, sécurité, monitoring, réseau	poetry install --extras "full-backend"
full-ai	NLP, OCR, pipelines, DuckDB	poetry install --extras "full-ai"
full-dev	Outils dev, CLI, UI, tests	poetry install --extras "full-dev"
db-sync	SQLAlchemy + psycopg2	poetry install --extras "db-sync"
db-async	SQLAlchemy + asyncpg	poetry install --extras "db-async"
firestore	Intégration Google Firestore	poetry install --extras "firestore"
security	Authentification et cryptographie	poetry install --extras "security"
monitoring	Prometheus, Sentry, psutil, OpenTelemetry	poetry install --extras "monitoring"
workers	Celery, Redis, cron, Flower	poetry install --extras "workers"
cli	CLI interactive (Typer, Click, Rich)	poetry install --extras "cli"
ui	Visualisation (Streamlit, Plotly, Pandas)	poetry install --extras "ui"
nlp	Traitement du langage naturel	poetry install --extras "nlp"
ocr	OCR et traitement PDF	poetry install --extras "ocr"
data	Pipelines, DuckDB, SQLModel, datasets	poetry install --extras "data"
📂 Structure du projet
Code
OliPLUS/
├── backend/         # API FastAPI
├── frontend/        # UI Streamlit
├── config/          # Configurations
├── devtools/        # Outils dev
├── tests/           # Tests
├── logs/            # Logs
├── Makefile         # Commandes cockpit
├── pyproject.toml   # Dépendances
└── README.md        # Documentation
⚙️ Commandes Makefile
makefile
install-core: poetry install --extras "core"
install-backend: poetry install --extras "full-backend"
install-ai: poetry install --extras "full-ai"
install-dev: poetry install --extras "full-dev"
install-nlp: poetry install --extras "nlp"
install-ocr: poetry install --extras "ocr"
install-ui: poetry install --extras "ui"
install-workers: poetry install --extras "workers"
install-monitoring: poetry install --extras "monitoring"

lint:
    ruff check .
    black --check .
    isort --check-only .

format:
    black .
    isort .

test:
    pytest

run-backend:
    uvicorn backend.main:app --reload

streamlit-ui:
    streamlit run frontend/dashboard.py

precommit:
    pre-commit run --all-files
🧪 Tests et lint
bash
make test        # Lance les tests Pytest
make lint        # Vérifie le style avec Ruff, Black, Isort
make format      # Formate automatiquement le code
make precommit   # Exécute les hooks Pre-commit
🔧 Extensions possibles
🔍 MkDocs pour documentation web

🧬 Streamlit cockpit pour pilotage visuel

🛠️ GitHub Actions pour CI/CD

🧠 Copilot CLI pour exécution à la volée

📜 Licence
Projet sous licence MIT — libre de l’utiliser, le modifier et le distribuer.

</details>

<details> <summary>🇬🇧 English</summary>

✨ Key Features
🔧 Backend API with FastAPI

📊 Interactive dashboard powered by Streamlit

🧠 Advanced NLP (Transformers, spaCy, NLTK)

📄 OCR & PDF processing (ocrmypdf, pytesseract)

🔍 Monitoring & observability (Prometheus, Sentry, OpenTelemetry)

🧬 Data pipelines with DuckDB and SQLModel

🔐 Authentication & enhanced security

🧪 Integrated devtools (tests, linting, type-checking, pre-commit)

🚀 Quick Installation
Install all cockpit modules:

bash
poetry install --extras "core full-backend full-ai full-dev"
Or by domain:

bash
poetry install --extras "nlp ocr ui dev"
📦 Cockpit Modules
Group	Description	Command
core	Minimal backend (FastAPI, uvicorn, loguru)	poetry install --extras "core"
full-backend	API, security, monitoring, networking	poetry install --extras "full-backend"
full-ai	NLP, OCR, pipelines, DuckDB	poetry install --extras "full-ai"
full-dev	Devtools, CLI, UI, tests	poetry install --extras "full-dev"
db-sync	SQLAlchemy + psycopg2	poetry install --extras "db-sync"
db-async	SQLAlchemy + asyncpg	poetry install --extras "db-async"
firestore	Google Firestore integration	poetry install --extras "firestore"
security	Authentication & cryptography	poetry install --extras "security"
monitoring	Prometheus, Sentry, psutil, OpenTelemetry	poetry install --extras "monitoring"
workers	Celery, Redis, cron, Flower	poetry install --extras "workers"
cli	Interactive CLI (Typer, Click, Rich)	poetry install --extras "cli"
ui	Visualization (Streamlit, Plotly, Pandas)	poetry install --extras "ui"
nlp	Natural language processing	poetry install --extras "nlp"
ocr	OCR & PDF processing	poetry install --extras "ocr"
data	Pipelines, DuckDB, SQLModel, datasets	poetry install --extras "data"
📂 Project Structure
Code
OliPLUS/
├── backend/         # FastAPI backend
├── frontend/        # Streamlit UI
├── config/          # Config files
├── devtools/        # Dev tools
├── tests/           # Unit & integration tests
├── logs/            # Execution logs
├── Makefile         # Cockpit commands
├── pyproject.toml   # Dependencies
└── README.md        # Documentation

⚙️ Makefile Commands
makefile
install-core: poetry install --extras "core"
install-backend: poetry install --extras "full-backend"
install-ai: poetry install --extras "full-ai"
install-dev: poetry install --extras "full-dev"
install-nlp: poetry install --extras "nlp"
install-ocr: poetry install --extras "ocr"
install-ui: poetry install --extras "ui"
install-workers: poetry install --extras "workers"
install-monitoring: poetry install --extras "monitoring"

lint:
    ruff check .
    black --check .
    isort --check-only .

format:
    black .
    isort .

test:
    pytest

run-backend:
    uvicorn backend.main:app --reload

streamlit-ui:
    streamlit run frontend/dashboard.py

precommit:
    pre-commit run --all-files
🧪 Testing & Linting
bash
make test        # Run Pytest
make lint        # Check style with Ruff, Black, Isort
make format      # Auto-format code
make precommit   # Run all pre-commit hooks
🔧 Possible Extensions
🔍 MkDocs for generating web documentation

🧬 Streamlit cockpit for visual module control

🛠️ GitHub Actions for CI/CD and automated testing

🧠 Copilot CLI for on-demand module execution

Cockpit Roadmap:

[ ] LangChain integration for NLP agents

[ ] Multi-user support with OAuth2

[ ] Automated PDF export from Streamlit

[ ] AI-powered scheduling module (cron + AI)

[ ] Voice-controlled cockpit dashboard

📜 License
Licensed under the MIT License — free to use, modify, and distribute.

</details>

Code

---

💡 Ce bloc est maintenant **complet** :  
- L’onglet **🇫🇷 Français** est déjà prêt dans la partie précédente  
- L’onglet **🇬🇧 English** est terminé avec toutes les sections  
- Les commandes Makefile sont complètes et identiques dans les deux langues  
- La mise en page est optimisée pour GitHub avec `<details>` et `<summary>`  