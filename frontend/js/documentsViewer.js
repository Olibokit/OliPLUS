let allDocuments = [];
let filteredDocuments = [];

const code = getQueryParam('code') || '0000';
const endpoint = `/structure/${code}`;

fetch(endpoint)
  .then(res => {
    if (!res.ok) throw new Error(`Erreur serveur: ${res.status}`);
    return res.json();
  })
  .then(data => {
    allDocuments = Array.isArray(data) ? data : [];
    filteredDocuments = [...allDocuments];
    renderDocuments(filteredDocuments);
  })
  .catch(err => {
    console.error("❌ Échec de récupération des documents:", err);
    document.getElementById('documentContainer').innerHTML = `
      <p class="text-center text-red-500">Erreur de chargement des documents.</p>
    `;
  });

function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

function applyFilters() {
  const auteur = document.getElementById('auteurFilter').value.trim().toLowerCase();
  const statut = document.getElementById('statutFilter').value;
  const minScore = parseInt(document.getElementById('scoreFilter').value || '0', 10);
  const dateMin = document.getElementById('dateMinFilter').value;

  filteredDocuments = allDocuments.filter(doc => {
    const matchAuteur = !auteur || (doc.auteur && doc.auteur.toLowerCase().includes(auteur));
    const matchStatut = !statut || doc.cycle_vie === statut;
    const matchScore = typeof doc.score !== 'number' || doc.score >= minScore;
    const matchDate = !dateMin || new Date(doc.date_creation) >= new Date(dateMin);

    return matchAuteur && matchStatut && matchScore && matchDate;
  });

  renderDocuments(filteredDocuments);
}

function resetFilters() {
  document.getElementById('auteurFilter').value = '';
  document.getElementById('statutFilter').value = '';
  document.getElementById('scoreFilter').value = '';
  document.getElementById('dateMinFilter').value = '';
  filteredDocuments = [...allDocuments];
  renderDocuments(filteredDocuments);
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return isNaN(date) ? '—' : date.toLocaleDateString();
}

function renderDocuments(documents) {
  const container = document.getElementById('documentContainer');
  container.innerHTML = '';

  if (documents.length === 0) {
    container.innerHTML = `<p class="text-center text-gray-500">Aucun document trouvé pour ce segment.</p>`;
    return;
  }

  const count = document.createElement('p');
  count.className = 'text-sm text-gray-500 mb-2';
  count.textContent = `${documents.length} document(s) affiché(s)`;
  container.appendChild(count);

  documents.forEach(doc => {
    const block = document.createElement('div');
    block.className = 'module-block';

    const title = document.createElement('div');
    title.className = 'module-title';
    title.textContent = doc.titre || 'Sans titre';

    const meta = document.createElement('div');
    meta.className = 'text-sm text-gray-600';
    meta.innerHTML = `
      Statut: <span class="font-semibold">${doc.cycle_vie || '—'}</span> · 
      Auteur: <span class="font-semibold">${doc.auteur || 'N/A'}</span> · 
      Score: <span class="font-semibold">${doc.score ?? '—'}</span> · 
      Date: ${formatDate(doc.date_creation)}
    `;

    const desc = document.createElement('div');
    desc.className = 'module-description';
    desc.textContent = doc.description || '';

    block.appendChild(title);
    block.appendChild(meta);
    block.appendChild(desc);

    container.appendChild(block);
  });
}

function exportDocuments(format = 'json') {
  const data = format === 'csv' ? toCSV(filteredDocuments) : JSON.stringify(filteredDocuments, null, 2);
  const blob = new Blob([data], { type: format === 'csv' ? 'text/csv' : 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `documents_export.${format}`;
  a.click();
  URL.revokeObjectURL(url);
}

function toCSV(docs) {
  if (!docs.length) return '';
  const headers = Object.keys(docs[0]);
  const rows = docs.map(doc => headers.map(h => `"${(doc[h] ?? '').toString().replace(/"/g, '""')}"`).join(','));
  return [headers.join(','), ...rows].join('\n');
}

// 🔍 Recherche en temps réel
document.getElementById('auteurFilter').addEventListener('keyup', applyFilters);

// 🔁 Bouton reset
document.getElementById('resetFiltersBtn').addEventListener('click', resetFilters);

// 📤 Boutons export
document.getElementById('exportJsonBtn').addEventListener('click', () => exportDocuments('json'));
document.getElementById('exportCsvBtn').addEventListener('click', () => exportDocuments('csv'));
