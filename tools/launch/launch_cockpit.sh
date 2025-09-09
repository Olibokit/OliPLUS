#!/bin/bash

# ┌────────────────────────────────────────────┐
# │      OIPLUS Cockpit Launch Script v0.2     │
# └────────────────────────────────────────────┘

MODE=${1:-dev}  # Mode par défaut : dev
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/cockpit-launch-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$LOG_DIR"

echo -e "\e[36m[COCKPIT] 🚀 Lancement du cockpit en mode: $MODE\e[0m" | tee -a "$LOG_FILE"

# Étape 1: Vérification de l’environnement
echo -e "\e[33m[COCKPIT] 🔍 Vérification de l’environnement...\e[0m" | tee -a "$LOG_FILE"
python3 sh/env_check_runner.py >> "$LOG_FILE" 2>&1 || {
  echo -e "\e[31m[ERREUR] Environnement non valide. Arrêt du lancement.\e[0m" | tee -a "$LOG_FILE"
  exit 1
}

# Étape 2: Nettoyage
echo -e "\e[33m[COCKPIT] 🧹 Nettoyage Docker et modules obsolètes...\e[0m" | tee -a "$LOG_FILE"
bash sh/purge_docker_logs.sh >> "$LOG_FILE" 2>&1
bash sh/purge_external_submodules.sh >> "$LOG_FILE" 2>&1

# Étape 3: Build des images cockpit
echo -e "\e[33m[COCKPIT] 🏗️ Construction des images Docker...\e[0m" | tee -a "$LOG_FILE"
bash sh/build_cockpit_images.sh >> "$LOG_FILE" 2>&1

# Étape 4: Compilation des traductions (si présentes)
if [ -f sh/compile_translations.sh ]; then
  echo -e "\e[33m[COCKPIT] 🌐 Compilation des traductions...\e[0m" | tee -a "$LOG_FILE"
  bash sh/compile_translations.sh >> "$LOG_FILE" 2>&1
fi

# Étape 5: Vérification de la santé
echo -e "\e[33m[COCKPIT] 🧪 Vérification de la santé du cockpit...\e[0m" | tee -a "$LOG_FILE"
bash sh/test_cockpit_health.sh >> "$LOG_FILE" 2>&1

# Étape 6: Lancement des services
echo -e "\e[33m[COCKPIT] 🔧 Démarrage des services via Docker Compose...\e[0m" | tee -a "$LOG_FILE"
docker-compose -f docker-compose.yml up --build -d >> "$LOG_FILE" 2>&1

# Résumé final
echo -e "\e[32m[COCKPIT] ✅ Tous les modules sont lancés avec succès.\e[0m" | tee -a "$LOG_FILE"
echo -e "\e[36m[COCKPIT] 📊 Accès au dashboard : http://localhost:8501\e[0m" | tee -a "$LOG_FILE"
