# SGHL — démarrage backend (port 8001, évite le conflit avec mon_projet_mongo sur 8000)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
Write-Host "SGHL backend -> http://127.0.0.1:8001/api/sante" -ForegroundColor Cyan
python manage.py runserver 8001
