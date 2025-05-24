# Prüfe und installiere Python-Abhängigkeiten
Write-Host "Prüfe und installiere Python-Abhängigkeiten..." -ForegroundColor Green
python -m pip install --upgrade pip
pip install fastapi uvicorn[standard]
pip install -r requirements.txt

# Installiere Frontend-Abhängigkeiten
Write-Host "Installiere Frontend-Abhängigkeiten..." -ForegroundColor Green
Set-Location webapp/frontend
npm install
npm install react-scripts --save-dev
Set-Location ../..

Write-Host "Starte die Server..." -ForegroundColor Green

# Starte Backend-Server
Write-Host "Starte Backend-Server..." -ForegroundColor Green
$backendJob = Start-Process -NoNewWindow powershell -ArgumentList "-Command", "Set-Location webapp/backend; python -m uvicorn main:app --reload --port 8000" -PassThru

# Starte Frontend-Server
Write-Host "Starte Frontend-Server..." -ForegroundColor Green
$frontendJob = Start-Process -NoNewWindow powershell -ArgumentList "-Command", "Set-Location webapp/frontend; npx react-scripts start" -PassThru

Write-Host "`nServer wurden gestartet!" -ForegroundColor Green
Write-Host "Frontend läuft auf: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend läuft auf:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "`nDrücken Sie Ctrl+C um beide Server zu beenden..." -ForegroundColor Yellow

# Warte auf Ctrl+C
try {
    Wait-Event -Timeout ([Int32]::MaxValue)
} finally {
    # Beende beide Server
    if ($null -ne $backendJob) { Stop-Process -Id $backendJob.Id -Force }
    if ($null -ne $frontendJob) { Stop-Process -Id $frontendJob.Id -Force }
    Write-Host "`nServer wurden beendet." -ForegroundColor Green
}
