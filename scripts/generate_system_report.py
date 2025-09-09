import os
from datetime import datetime

report_path = r"C:\Users\Olibokit\OliPLUS\logs\system_report.html"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Simulations d'état avant/après
components = {
    "Python": ("3.9.1 ⚠️", "3.11.4 ✅"),
    "Streamlit": ("❌", "1.32.0 ✅"),
    "Docker": ("❌", "✅"),
    "Django": ("3.2 ✅", "4.2 ✅"),
    "Windows Update": ("⚠️", "✅"),
    "Intel Drivers": ("❌", "✅")
}

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport Système - OliPLUS</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            color: #333;
            margin: 20px;
        }}
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #1e1e1e;
                color: #ddd;
            }}
            table {{
                background-color: #2c2c2c;
                color: #ddd;
            }}
        }}
        h2 {{
            text-align: center;
        }}
        table {{
            width: 80%;
            margin: auto;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            border: 1px solid #999;
            text-align: center;
        }}
        th {{
            background-color: #555;
            color: white;
        }}
        .timestamp {{
            text-align: center;
            margin-bottom: 20px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <h2>📊 Rapport Système - OliPLUS</h2>
    <div class="timestamp">Généré le : {timestamp}</div>
    <table>
        <tr>
            <th>Composant</th>
            <th>Avant mise à jour</th>
            <th>Après mise à jour</th>
        </tr>"""

for comp, (before, after) in components.items():
    html += f"<tr><td>{comp}</td><td>{before}</td><td>{after}</td></tr>"

html += """
    </table>
</body>
</html>
"""

with open(report_path, "w", encoding="utf-8") as f:
    f.write(html)
