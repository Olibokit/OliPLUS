import streamlit as st
import getpass
import shutil
import re
from pathlib import Path
from datetime import datetime

# --- Configuration ---
SOURCE_DIR = Path("verification")
DEST_ROOT = Path("classified_files")
DEST_ROOT.mkdir(exist_ok=True)
EMPTY_THRESHOLD = 5

# 🧩 Extensions par catégorie
CODE_EXTENSIONS = [".py", ".pyd", ".pyi", ".js", ".ts", ".sh"]
CONFIG_EXTENSIONS = [".json", ".jsons", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".env", ".toml", ".lock", ".spec", ".nupkg"]
DOC_EXTENSIONS = [".md", ".txt", ".html", ".css", ".in"]
LOG_EXTENSIONS = [".log", ".csv", ".xlm"]
IGNORED_EXTENSIONS = [".pdf", ".docx", ".jpg", ".png", ".jpeg"]

HIGH_RISK_EXTENSIONS = [".lock", ".nupkg", ".pyd", ".pyi", ".spec", ".jsons"]

PRIORITY_EXTENSIONS = CODE_EXTENSIONS + CONFIG_EXTENSIONS + DOC_EXTENSIONS + LOG_EXTENSIONS

SEMANTIC_RULES = {
    "scripts_py": "Scripts Python",
    "config_json": "Configurations JSON",
    "config_yaml": "Configurations YAML",
    "docs_md": "Documentation Markdown",
    "notes": "Notes de réunion",
    "à_classer": "À classer"
}

# --- Fonctions utilitaires ---
def read_file_content(file_path):
    """
    Lit le contenu d'un fichier en gérant les erreurs d'encodage.
    """
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def is_effectively_empty(file):
    """
    Détermine si un fichier est vide ou contient très peu de contenu significatif.
    """
    content = read_file_content(file).strip()
    lines = content.splitlines()
    return len(lines) < EMPTY_THRESHOLD or all(len(line.strip()) == 0 for line in lines) or len(content) < 20

def should_analyze(file):
    """
    Vérifie si le fichier doit être analysé en fonction de son extension.
    """
    return file.suffix.lower() in PRIORITY_EXTENSIONS

def is_high_risk(file):
    """
    Vérifie si le fichier a une extension à haut risque.
    """
    return file.suffix.lower() in HIGH_RISK_EXTENSIONS

def classify_by_content(file):
    """
    Classifie un fichier en fonction de son contenu et de son extension.
    """
    content = read_file_content(file).lower()
    if "def " in content or "import " in content:
        return "Scripts Python"
    elif file.suffix == ".json":
        return "Configurations JSON"
    elif file.suffix in [".yaml", ".yml"]:
        return "Configurations YAML"
    elif "# " in content or "## " in content:
        return "Documentation Markdown"
    elif "meeting" in content or "minutes" in content:
        return "Notes de réunion"
    return "À classer"

def detect_functionality(content):
    """
    Détecte la fonctionnalité principale d'un script à partir de mots-clés.
    """
    content = content.lower()
    if "launch_task" in content or "awx" in content:
        return "Déclencheur AWX"
    elif "pandas" in content or "plot" in content:
        return "Exploration de données"
    elif "os.environ" in content or "settings" in content:
        return "Configuration"
    elif "unittest" in content or "assert" in content:
        return "Test"
    elif "audit" in content or "log" in content:
        return "Audit"
    else:
        return "Inconnu"

def score_script(content):
    """
    Calcule un score de confiance pour un script en évaluant plusieurs critères.
    """
    score = 0
    # Utilisation d'une chaîne brute (raw string) pour éviter les SyntaxWarning
    if len(re.findall(r"def\s+\w+\(.*?\):", content)) >= 1:
        score += 25
    if all(len(name) > 2 for name in re.findall(r"\b\w+\b", content)):
        score += 25
    try:
        compile(content, "<string>", "exec")
        score += 25
    except:
        pass
    if '"""' in content or "#" in content:
        score += 25
    return score

def get_score_color(score):
    """
    Renvoie une étiquette de couleur pour le score.
    """
    if score >= 85:
        return "🟢 Très fiable"
    elif score >= 70:
        return "🟡 Fiabilité moyenne"
    elif score >= 50:
        return "🟠 À surveiller"
    else:
        return "🔴 Faible confiance"

def render_score_bar(score):
    """
    Affiche une barre de progression stylisée pour le score.
    """
    color = "#4CAF50" if score >= 85 else "#FFC107" if score >= 70 else "#FF9800" if score >= 50 else "#F44336"
    return f"""
    <div style='background-color:{color}; width:{score}%; padding:4px; color:white; text-align:center; border-radius:4px'>
        Score de confiance : {score}/100
    </div>
    """

# --- Interface Streamlit ---
st.set_page_config(page_title="Organisateur de Fichiers Intelligent", layout="wide")
st.title("🗂️ Organisateur de Fichiers Intelligent")
st.markdown("---")

# 🔒 Utilisateur
st.sidebar.markdown("### 🔒 Statut de l'utilisateur")
try:
    USER = getpass.getuser()
    st.sidebar.info(f"👤 Utilisateur : `{USER}`")
except Exception:
    st.sidebar.info(f"👤 Utilisateur : `utilisateur_anonyme`")

# 📚 Règles sémantiques
st.sidebar.markdown("---")
with st.sidebar.expander("📚 Règles sémantiques"):
    for k, v in SEMANTIC_RULES.items():
        st.markdown(f"- `{k}` → **{v}**")

# 🔍 Scan des fichiers
all_files = [f for f in SOURCE_DIR.rglob("*") if f.is_file()]
analyzable_files = [f for f in all_files if should_analyze(f)]
empty_files = [f for f in all_files if is_effectively_empty(f)]

st.sidebar.markdown(f"### 📁 Fichiers détectés : `{len(all_files)}`")
st.sidebar.markdown(f"- Fichiers analysables : `{len(analyzable_files)}`")
st.sidebar.markdown(f"- Fichiers vides : `{len(empty_files)}`")

# 🧹 Nettoyage des fichiers vides
if empty_files:
    st.sidebar.warning(f"{len(empty_files)} fichier(s) vide(s) ou corrompu(s) détecté(s)")
    if st.sidebar.button("🧹 Supprimer les fichiers vides"):
        for f in empty_files:
            try:
                f.unlink()
            except Exception as e:
                st.sidebar.error(f"Erreur lors de la suppression de `{f.name}`: {e}")
        st.sidebar.success("Fichiers vides supprimés ✅")
        st.rerun()

# 📦 Reclassification manuelle
st.header("📦 Reclassification Manuelle (Quarantaine)")
quarantine_files = [f for f in analyzable_files if "verifier" in f.name or "inconnue" in f.name]
if quarantine_files:
    for i, f in enumerate(quarantine_files):
        st.markdown(f"**Fichier :** `{f.name}`")
        with st.container(border=True):
            suggested = classify_by_content(f)
            new_cat = st.selectbox(
                "📂 Reclasser vers...",
                options=list(SEMANTIC_RULES.values()),
                index=list(SEMANTIC_RULES.values()).index(suggested) if suggested in SEMANTIC_RULES.values() else 0,
                key=f"select_{i}"
            )
            if st.button(f"📦 Reclasser dans `{new_cat}`", key=f"manual_reclass_{i}"):
                dest_path = DEST_ROOT / new_cat / f.name
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.move(str(f), str(dest_path))
                    st.success(f"`{f.name}` déplacé vers `{new_cat}` ✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Échec du déplacement de `{f.name}`: {e}")
else:
    st.info("Aucun fichier à reclasser manuellement.")

st.markdown("---")

# --- NOUVELLE SECTION ---
st.header("🟢 Fichiers très fiables (score ≥ 95)")
for f in analyzable_files:
    content = read_file_content(f)
    score = score_script(content)
    if score >= 95:
        st.markdown(f"✅ `{f.name}` | Score : {score}/100")
        st.markdown(render_score_bar(score), unsafe_allow_html=True)
st.markdown("---")

# 🧪 Mode Audit
st.header("🧪 Mode Audit (Simulation)")
dry_run = st.checkbox("Activer le mode Audit")
min_score = st.slider("🎯 Filtrer les fichiers par score minimum", min_value=0, max_value=100, value=60, step=5)

if st.button("Lancer la simulation de classification"):
    if dry_run:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path(f"audit_{timestamp}.log")

        st.info("Mode Audit activé. Simulation en cours...")
        simulated_actions = []

        for f in analyzable_files:
            content = read_file_content(f)
            category = classify_by_content(f)
            function = detect_functionality(content)
            score = score_script(content)

            if score >= min_score:
                score_label = get_score_color(score)
                line = f"[DRY-RUN] `{f.name}` → Catégorie : `{category}` | Fonction : `{function}` | Score : `{score}/100` {score_label}"
                simulated_actions.append(line)

                st.markdown(f"- {line}")
                st.markdown(render_score_bar(score), unsafe_allow_html=True)

                if is_high_risk(f):
                    st.warning(f"⚠️ `{f.name}` est un fichier à extension critique : `{f.suffix}`")

        for f in empty_files:
            line = f"[DRY-RUN] Supprimer `{f.name}` (fichier vide)"
            simulated_actions.append(line)
            st.markdown(f"- {line}")

        st.info(f"{len(simulated_actions)} action(s) simulée(s) avec score ≥ {min_score}")

        with open(log_path, "w", encoding="utf-8") as log:
            log.write("\n".join(simulated_actions))

        with open(log_path, "rb") as f:
            st.download_button("📥 Télécharger le rapport d'audit", f, file_name=log_path.name)

        st.success(f"Audit terminé. Rapport généré dans `{log_path.name}` ✅")
    else:
        st.warning("Veuillez activer le mode Audit pour lancer la simulation.")

st.markdown("---")

# 📦 Reclassification Automatique
st.header("📦 Reclassification Automatique")
if st.button("Reclasser les fichiers très fiables (score ≥ 85)"):
    reclassed_count = 0
    for f in analyzable_files:
        content = read_file_content(f)
        score = score_script(content)
        if score >= 85:
            category = classify_by_content(f)
            dest_path = DEST_ROOT / category / f.name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(f), str(dest_path))
                reclassed_count += 1
            except Exception as e:
                st.error(f"Erreur lors du déplacement de `{f.name}` : {e}")
    st.success(f"{reclassed_count} fichier(s) très fiable(s) reclassé(s) automatiquement ✅")
    st.rerun()

st.header("🔍 Fichiers à surveiller")
suspicious_files = []

for f in analyzable_files:
    content = read_file_content(f)
    score = score_script(content)
    # L'opérateur not est utilisé ici à la place de l'opérateur ~ qui est déprécié pour les booléens.
    if not (score >= 50) or is_high_risk(f):
        suspicious_files.append((f.name, score, f.suffix))

if suspicious_files:
    for name, score, ext in suspicious_files:
        st.markdown(f"- ⚠️ `{name}` | Score : `{score}` | Extension : `{ext}`")
        st.markdown(render_score_bar(score), unsafe_allow_html=True)
else:
    st.info("Aucun fichier critique ou douteux détecté.")
