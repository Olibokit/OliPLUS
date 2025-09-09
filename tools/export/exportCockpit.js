// exportCockpit.js

const cockpitData = [
  ["Module", "Statut"],
  ["OCR", "✅ OK"],
  ["NLP", "🟡 En cours"]
];

function generateCSV(data) {
  return data.map(row => row.join(",")).join("\n");
}

function downloadFile(blob, filename) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
}

function exportCSV() {
  const csvContent = generateCSV(cockpitData);
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  downloadFile(blob, "cockpit_export.csv");
}

function exportXLSX() {
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(cockpitData);
  XLSX.utils.book_append_sheet(wb, ws, "Cockpit");
  XLSX.writeFile(wb, "cockpit_export.xlsx");
}

// 🧪 Test cockpit : exportCSV() et exportXLSX() doivent générer des fichiers valides
