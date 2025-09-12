import os
import json
import ast
from pathlib import Path
from datetime import datetime

# === PARAMÈTRES ===
SCAN_DIRS = ["apps/", "backends/", "frontend/", "dashboard/", "test/", "oliplus_toolchain/"]
EXTENSIONS = [".py", ".html"]
KEYWORDS_MAP = {
    "upload": ["upload", "file", "ingestion"],
    "dashboard": ["streamlit", "kpi", "chart"],
    "routes": ["@app.route", "@router", "FastAPI"],
    "template": ["html", "template", "jinja"],
    "legacy": ["legacy", "deprecated"],
    "visual": ["streamlit", "plotly", "matplotlib"],
}


# === FONCTIONS UTILITAIRES ===

def extract_py_components(file_path):
    classes = []
    functions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            node = ast.parse(f.read(), filename=file_path)
            for n in node.body:
                if isinstance(n, ast.ClassDef):
                    classes.append(n.name)
                elif isinstance(n, ast.FunctionDef):
                    functions.append(n.name)
    except Exception:
        pass
    return classes, functions

def extract_keywords(file_path, content):
    words = []
    lower = content.lower()
    for key, terms in KEYWORDS_MAP.items():
        if any(t in lower for t in terms):
            words.append(key)
    return words

def get_status(keywords):
    if "legacy" in keywords:
        return "à refondre"
    elif "dashboard" in keywords or "visual" in keywords:
        return "à conserver"
    return "à clarifier"

# === SCAN PRINCIPAL ===

def analyse_codebase(base_path="."):
    report = {
        "scan_id": f"scan_{datetime.now().strftime('%Y-%m-%d_%H%M')}",
        "scan_timestamp": datetime.utcnow().isoformat() + "Z",
        "scanned_directories": SCAN_DIRS,
        "files_analysis": [],
    }

    for folder in SCAN_DIRS:
        for root, _, files in os.walk(folder):
            for file in files:
                ext = Path(file).suffix
                if ext not in EXTENSIONS:
                    continue
                file_path = os.path.join(root, file)
                try:
                    content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue

                keywords = extract_keywords(file_path, content)
                classes, functions = extract_py_components(file_path) if ext == ".py" else ([], [])
                status = get_status(keywords)

                analysis = {
                    "path": file_path,
                    "filename": file,
                    "extension": ext,
                    "size_bytes": Path(file_path).stat().st_size,
                    "last_modified": datetime.fromtimestamp(Path(file_path).stat().st_mtime).isoformat(),
                    "type": "Python" if ext == ".py" else "HTML",
                    "identified_keywords": keywords,
                    "components": {
                        "classes": classes,
                        "functions": functions,
                        "routes": [f for f in functions if "route" in f.lower()],
                        "templates": [file] if ext == ".html" else [],
                    },
                    "status": status,
                    "notes": ""
                }
                report["files_analysis"].append(analysis)

    return report


# === SAUVEGARDE ===

def save_report(report):
    suffix = datetime.now().strftime("%Y%m%d-%H%M")
    output_path = Path("cockpit_rapports/scans/") / f"codebase_scan_{suffix}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"✅ Rapport sauvegardé : {output_path.resolve()}")

# === LANCEMENT ===

if __name__ == "__main__":
    print("🧠 Analyse du code cockpit en cours…")
    rapport = analyse_codebase()
    save_report(rapport)
