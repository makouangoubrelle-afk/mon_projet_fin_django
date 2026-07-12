# SGHL — Démarrage rapide (Windows)
Write-Host "=== SGHL : démarrage backend + frontend ===" -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# Libérer le port 5173 si un ancien Vite tourne encore
$on5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($on5173) {
  Write-Host "Port 5173 occupé — fermeture de l'ancien processus..." -ForegroundColor Yellow
  $on5173 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
  Start-Sleep -Seconds 1
}

Write-Host "Backend Django sur http://127.0.0.1:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; python manage.py runserver 8000"

Start-Sleep -Seconds 2

Write-Host "Frontend Vue sur http://localhost:5173/login" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\sih-frontend'; npm run dev"

Write-Host ""
Write-Host "Ouvrez exactement : http://localhost:5173/login" -ForegroundColor Yellow
Write-Host "Cliquez sur Administrateur (admin@sghl.com)" -ForegroundColor Yellow
