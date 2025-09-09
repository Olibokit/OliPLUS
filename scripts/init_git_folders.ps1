# 🛠️ Initialisation cockpit des répertoires stratégiques
$startTime = Get-Date
Write-Host "`n🔧 Initialisation cockpit des répertoires stratégiques — $startTime" -ForegroundColor Magenta

# 📦 Répertoires à initialiser
$folders = @(
    "media",
    "staticfiles",
    "logs",
    "apps/ventes/migrations",
    "apps/livres/migrations",
    "apps/users/migrations",
    "templates",
    "frontend/dashboard/build"
)

# 📊 Compteurs cockpit
$createdDirs = 0
$addedGitkeeps = 0
$errors = @()

# 🔁 Boucle d’initialisation cockpit
foreach ($folder in $folders) {
    $folderDisplay = $folder.Replace("/", "\")  # Compatibilité Windows

    try {
        if (-not (Test-Path $folderDisplay)) {
            New-Item -ItemType Directory -Path $folderDisplay -Force | Out-Null
            Write-Host "📁 Dossier créé     :" $folderDisplay -ForegroundColor Cyan
            $createdDirs++
        } else {
            Write-Host "✔️ Dossier existant :" $folderDisplay -ForegroundColor DarkGray
        }

        $gitkeepPath = Join-Path $folderDisplay ".gitkeep"

        if (-not (Test-Path $gitkeepPath)) {
            Set-Content -Path $gitkeepPath -Value "# Keep this directory tracked by Git" -Force
            Write-Host "➕ .gitkeep ajouté   dans :" $folderDisplay -ForegroundColor Green
            $addedGitkeeps++
        } else {
            Write-Host "🔁 .gitkeep présent dans  :" $folderDisplay -ForegroundColor Yellow
        }
    } catch {
        $errors += "❌ Erreur sur $folderDisplay : $_"
    }
}

# 🧭 Vérification Git cockpit
if (-not (Test-Path ".git")) {
    Write-Host "`n⚠️ Attention : le dossier courant n’est pas un dépôt Git cockpitifié." -ForegroundColor Red
} else {
    Write-Host "`n✅ Dépôt Git détecté — traçabilité cockpit activée." -ForegroundColor Green
}

# 📋 Résumé cockpit
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "`n─────────────────────────────────────────────"
Write-Host "`n🧾 Résumé cockpit :" -ForegroundColor Cyan
Write-Host "📁 $createdDirs dossier(s) créé(s)" -ForegroundColor Cyan
Write-Host "📌 $addedGitkeeps .gitkeep ajouté(s)" -ForegroundColor Cyan
Write-Host "⏱️ Durée d’exécution : $duration sec" -ForegroundColor Cyan

if ($errors.Count -gt 0) {
    Write-Host "`n🚨 Erreurs détectées :" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host $_ -ForegroundColor Red }
} else {
    Write-Host "`n✅ Tous les répertoires sont prêts à être versionnés avec Git.`n" -ForegroundColor Green
}
