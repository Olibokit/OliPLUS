import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 📈 Données CPU et RAM
labels = ["t0", "t1", "t2"]
cpu_values = [13.2, 17.6, 22.1]
ram_values = [46.3, 52.5, 63.0]

# 🔔 Seuils d'alerte
error_count = 2
provenance_score = 0.93

# 📊 Affichage des métriques
st.title("📊 Cockpit des métriques module MOD-OLI-001")

df = pd.DataFrame({
    "Label": labels,
    "CPU (%)": cpu_values,
    "RAM (MB)": ram_values
})

st.line_chart(df.set_index("Label"))

# 🔔 Alertes automatiques
if error_count > 3:
    st.error(f"❌ Trop d'erreurs détectées : {error_count}")
elif provenance_score < 0.8:
    st.warning(f"⚠️ Score de provenance faible : {provenance_score}")
else:
    st.success("✅ Aucun seuil critique détecté")

# 📌 Résumé
st.metric("Provenance Score", provenance_score)
st.metric("Error Count", error_count)
