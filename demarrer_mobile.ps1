# SGHL — Backend Django + app Flutter mobile (/mobile/)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "=== SGHL Mobile (Flutter) ===" -ForegroundColor Cyan

& "$Root\build_mobile.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Backend Django sur http://127.0.0.1:8001" -ForegroundColor Green
Write-Host "App Flutter   sur http://127.0.0.1:8001/mobile/" -ForegroundColor Green
Write-Host "Test patient  : patient@gmail.com + code OTP" -ForegroundColor Yellow
Write-Host ""

Start-Process "http://127.0.0.1:8001/mobile/"
python manage.py runserver 8001
