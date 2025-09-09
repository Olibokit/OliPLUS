# 🛩️ OILPLUS — Cockpit personnel d’automatisation

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Poetry](https://img.shields.io/badge/poetry-managed-8A2BE2)
![License](https://img.shields.io/badge/license-MIT-green)
![Build](https://img.shields.io/github/actions/workflow/status/toncompte/oliplus/ci.yml)

OILPLUS est un cockpit Python modulaire conçu pour orchestrer des tâches d’automatisation, de visualisation, de NLP, d’OCR, de monitoring, et bien plus.  
Il s’appuie sur **FastAPI**, **Streamlit**, **Transformers**, **DuckDB**, **Firestore**, et une panoplie d’outils cockpitifiés pour les développeurs exigeants.

---

## ✨ Fonctionnalités

- 🔧 API backend avec FastAPI
- 📊 Dashboard interactif avec Streamlit
- 🧠 NLP avancé (Transformers, spaCy, NLTK)
- 📄 OCR et traitement PDF (ocrmypdf, pytesseract)
- 🔍 Monitoring et observabilité (Prometheus, Sentry, OpenTelemetry)
- 🧬 Pipelines de données avec DuckDB et SQLModel
- 🔐 Authentification et sécurité renforcée
- 🧪 Devtools intégrés (tests, lint, type-check, pre-commit)

---

## 🧭 Sommaire

- 🚀 [Installation rapide](#installation-rapide)
- 📦 [Modules cockpit](#modules-cockpit)
- 📂 [Structure du projet](#structure-du-projet)
- ⚙️ [Commandes Makefile](#commandes-makefile)
- 🧪 [Tests et lint](#tests-et-lint)
- 🔧 [Extensions possibles](#extensions-possibles)

---

## 🚀 Installation rapide

Installe tous les modules cockpitifiés :

```bash
poetry install --extras "core full-backend full-ai full-dev"
Ou installe par domaine :

bash
poetry install --extras "nlp ocr ui dev"
📦 Modules cockpit
Groupe	Description	Commande d’installation
core	Backend minimal (FastAPI, uvicorn, loguru)	poetry install --extras "core"
full-backend	API, sécurité, monitoring, réseau	poetry install --extras "full-backend"
full-ai	NLP, OCR, pipelines, DuckDB	poetry install --extras "full-ai"
full-dev	Devtools, CLI, UI, tests	poetry install --extras "full-dev"
db-sync	SQLAlchemy + psycopg2	poetry install --extras "db-sync"
db-async	SQLAlchemy + asyncpg	poetry install --extras "db-async"
firestore	Intégration Google Firestore	poetry install --extras "firestore"
security	Authentification et cryptographie étendue	poetry install --extras "security"
monitoring	Prometheus, Sentry, psutil, OpenTelemetry	poetry install --extras "monitoring"
workers	Celery, Redis, cron, Flower	poetry install --extras "workers"
cli	CLI interactive avec Typer, Click, Rich	poetry install --extras "cli"
ui	Visualisation avec Streamlit, Plotly, Pandas	poetry install --extras "ui"
nlp	Traitement du langage naturel étendu	poetry install --extras "nlp"
ocr	OCR et traitement de PDF	poetry install --extras "ocr"
data	Pipelines, DuckDB, SQLModel, datasets	poetry install --extras "data"
📂 Structure du projet
bash
OILPLUS/
├── backend/         # API FastAPI
│   ├── main.py
│   └── routes/
├── frontend/        # UI Streamlit
│   └── dashboard.py
├── config/          # Fichiers de configuration
│   └── settings.py
├── devtools/        # Scripts, Makefile, outils de dev
├── tests/           # Tests unitaires et d’intégration
├── logs/            # Logs d’exécution
├── Makefile         # Commandes cockpit
├── pyproject.toml   # Dépendances cockpitifiées
├── README.md        # Documentation cockpit
⚙️ Commandes Makefile
Ajoute ce fichier à la racine du projet : OILPLUS/Makefile

makefile
install-core:
    poetry install --extras "core"

install-backend:
    poetry install --extras "full-backend"

install-ai:
    poetry install --extras "full-ai"

install-dev:
    poetry install --extras "full-dev"

install-nlp:
    poetry install --extras "nlp"

install-ocr:
    poetry install --extras "ocr"

install-ui:
    poetry install --extras "ui"

install-workers:
    poetry install --extras "workers"

install-monitoring:
    poetry install --extras "monitoring"

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
🔍 MkDocs pour générer une documentation web

🧬 Streamlit cockpit pour piloter les modules visuellement

🛠️ GitHub Actions pour CI/CD et tests automatisés

🧠 Copilot CLI pour lancer des modules à la volée

🛣️ Roadmap cockpit
[ ] Intégration de LangChain pour agents NLP

[ ] Support multi-utilisateur avec OAuth2

[ ] Export PDF automatisé depuis Streamlit

[ ] Module de scheduling intelligent (cron + AI)

[ ] Dashboard cockpit pilotable par voix

📜 Licence
Ce projet est sous licence MIT. Tu es libre de l’utiliser, le modifier, le distribuer — cockpit ouvert, moteur allumé.