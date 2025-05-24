# Verzeichnis wechseln
Set-Location webapp/frontend

# Node-Module löschen
Write-Host "Lösche node_modules..." -ForegroundColor Yellow
if (Test-Path node_modules) {
    Remove-Item -Recurse -Force node_modules
}
if (Test-Path package-lock.json) {
    Remove-Item -Force package-lock.json
}

# Node-Module neu installieren
Write-Host "Installiere node_modules neu..." -ForegroundColor Green
npm install

# Zusätzliche Abhängigkeiten installieren
Write-Host "Installiere zusätzliche Abhängigkeiten..." -ForegroundColor Green
npm install @tanstack/react-query axios

# Frontend starten
Write-Host "Starte Frontend..." -ForegroundColor Green
npm start
