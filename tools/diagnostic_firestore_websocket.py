# diagnostic_firestore_websocket.py — cockpit Firestore + WebSocket + Streamlit + Logs

import asyncio
import websockets
from google.cloud import firestore
from google.api_core.exceptions import GoogleAPIError
from datetime import datetime
import os
import sys

# === 🔧 Journalisation cockpitifiée ===
def write_trace_log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = f"[{timestamp}][{level}]"
    log_line = f"{prefix} {message}"
    print(log_line)

    log_path = os.path.join("logs", "trace.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

# === 🔥 Test Firestore ===
def test_firestore_connection():
    try:
        db = firestore.Client()
        docs = db.collection("correctifs").limit(1).stream()
        for doc in docs:
            write_trace_log(f"✅ Firestore OK — Document trouvé : {doc.id}")
            return True
        write_trace_log("✅ Firestore OK — Collection vide mais accessible.")
        return True
    except GoogleAPIError as e:
        write_trace_log(f"❌ Firestore ERROR — {e}", level="ERROR")
        return False
    except Exception as e:
        write_trace_log(f"❌ Firestore Exception — {e}", level="ERROR")
        return False

# === 📡 Test WebSocket ===
async def test_websocket_connection():
    uri = "ws://localhost:8000/ws/correctifs"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send("ping")
            write_trace_log(f"✅ WebSocket OK — Connecté à {uri}")
            return True
    except Exception as e:
        write_trace_log(f"❌ WebSocket ERROR — {e}", level="ERROR")
        return False

# === 📊 Interface Streamlit cockpitifiée ===
def show_streamlit_dashboard(firestore_ok, websocket_ok):
    import streamlit as st

    st.set_page_config(page_title="Diagnostic cockpit", page_icon="🧪")
    st.title("🧪 Diagnostic Firestore / WebSocket")

    st.subheader("📊 Résultats cockpit")
    st.success("✅ Firestore connecté") if firestore_ok else st.error("❌ Firestore échec")
    st.success("✅ WebSocket opérationnel") if websocket_ok else st.error("❌ WebSocket échec")

    if firestore_ok and websocket_ok:
        st.markdown("🚀 Tout est prêt pour le cockpit OLI+")
    else:
        st.warning("⛔ Problème détecté — vérifiez les services ou les ports.")

# === 🚀 Lancement cockpit du diagnostic ===
if __name__ == "__main__":
    write_trace_log("🔍 Diagnostic cockpit Firestore + WebSocket lancé")

    firestore_ok = test_firestore_connection()
    websocket_ok = asyncio.run(test_websocket_connection())

    write_trace_log(f"📊 Résumé cockpit : Firestore={'OK' if firestore_ok else 'Échec'}, WebSocket={'OK' if websocket_ok else 'Échec'}")

    if "--streamlit" in sys.argv:
        show_streamlit_dashboard(firestore_ok, websocket_ok)
