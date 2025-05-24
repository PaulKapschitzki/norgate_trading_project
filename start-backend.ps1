# Absoluten Pfad zum Projektverzeichnis setzen
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = $projectRoot

Write-Host "Project Root: $projectRoot" -ForegroundColor Cyan
Write-Host "Python-Pfad gesetzt auf: $env:PYTHONPATH" -ForegroundColor Cyan

# Backend starten (vom Root-Verzeichnis aus)
Write-Host "Starte Backend..." -ForegroundColor Green
python -m webapp.backend.main
