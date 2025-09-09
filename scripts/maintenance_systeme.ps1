# 1. Vider la corbeille
Clear-RecycleBin -Force

# 2. Supprimer les fichiers temporaires système
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Nettoyage de disque (mode express)
Start-Process cleanmgr.exe -ArgumentList "/sagerun:1"

# 4. Défragmentation uniquement si le disque principal est un HDD
$drive = Get-PhysicalDisk | Where-Object MediaType -eq 'HDD'
if ($drive) {
    Write-Host "`n💽 Défragmentation en cours sur le disque système..."
    Optimize-Volume -DriveLetter C -Defrag -Verbose
} else {
    Write-Host "`n🚀 Pas de défragmentation nécessaire : disque SSD détecté."
}

# 5. Petite pause pour bien voir les résultats
Start-Sleep -Seconds 5
