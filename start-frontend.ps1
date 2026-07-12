# SGHL — démarrage frontend Vue (proxy API -> port 8001)
$Root = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "sih-frontend"
Set-Location $Root
Write-Host "SGHL frontend -> http://localhost:5173" -ForegroundColor Cyan
npm run dev
