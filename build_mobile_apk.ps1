# Build APK Android pointant vers l'API Render
Set-Location $PSScriptRoot\sih_mobile
flutter pub get
flutter build apk --release `
  --dart-define=API_BASE=https://mon-projet-fin-django.onrender.com/api
Write-Host ""
Write-Host "APK genere : sih_mobile\build\app\outputs\flutter-apk\app-release.apk" -ForegroundColor Green
