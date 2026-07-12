# Compile l'app Flutter Web -> mobile_dist/ (servie par Django sur /mobile/)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location "$Root\sih_mobile"

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    Write-Host "Flutter n'est pas installé." -ForegroundColor Red
    Write-Host "Installez-le : https://docs.flutter.dev/get-started/install/windows" -ForegroundColor Yellow
    Write-Host "Puis ajoutez C:\flutter\bin au PATH et relancez ce script." -ForegroundColor Yellow
    exit 1
}

Write-Host "=== Build SGHL Mobile (Flutter Web) ===" -ForegroundColor Cyan
flutter pub get
if (Test-Path "$Root\mobile_dist") {
    Remove-Item -Recurse -Force "$Root\mobile_dist"
}
flutter build web --release --base-href /mobile/ --output "$Root\mobile_dist"
Write-Host ""
Write-Host 'OK — mobile_dist/ pret.' -ForegroundColor Green
Write-Host 'Lancez Django puis ouvrez : http://127.0.0.1:8001/mobile/' -ForegroundColor Green
