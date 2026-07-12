# SGHL Mobile — Flutter

Application **patient** (connexion OTP + dossier médical).  
Elle est **déjà dans ce dépôt** et reliée au backend Django.

## Architecture

```
mon_projet_fin_django/
├── sih_mobile/          ← code source Flutter (Dart)
├── mobile_dist/         ← build Web compilé (généré)
├── sih-frontend/        ← interface web Vue (personnel + admin)
└── config/urls.py       ← Django sert /mobile/ depuis mobile_dist/
```

| Interface | Techno | URL locale | URL Render |
|-----------|--------|------------|------------|
| Personnel / Admin | Vue 3 | http://localhost:5173 | https://mon-projet-fin-django.onrender.com/ |
| Patient mobile | Flutter | http://127.0.0.1:8001/mobile/ | https://mon-projet-fin-django.onrender.com/mobile/ |

## Prérequis

- [Flutter SDK](https://docs.flutter.dev/get-started/install/windows) (stable)
- Backend Django démarré (port **8001**)

Vérifier : `flutter --version`

## Démarrage rapide (Windows)

Depuis la racine du projet :

```powershell
.\demarrer_mobile.ps1
```

Ou manuellement :

```powershell
.\build_mobile.ps1
python manage.py runserver 8001
# Ouvrir http://127.0.0.1:8001/mobile/
```

Connexion test : **patient@gmail.com** + code OTP affiché à l'écran.

## Développement Flutter (live reload)

Terminal 1 — API :

```powershell
python manage.py runserver 8001
```

Terminal 2 — Flutter :

```powershell
cd sih_mobile
flutter pub get
flutter run -d chrome --web-port 8080 --dart-define=API_BASE=http://127.0.0.1:8001/api
```

## APK Android

```powershell
.\build_mobile_apk.ps1
```

APK : `sih_mobile\build\app\outputs\flutter-apk\app-release.apk`

## Fichiers importants

| Fichier | Rôle |
|---------|------|
| `lib/main.dart` | Point d'entrée |
| `lib/screens/login_screen.dart` | Connexion OTP |
| `lib/screens/home_screen.dart` | Espace patient |
| `lib/config/api_config.dart` | URL API (`/api` ou Render) |
| `pubspec.yaml` | Dépendances Flutter |

## Déploiement Render

Render n'a pas Flutter installé : le dossier **`mobile_dist/`** est commité dans Git.  
À chaque modification Flutter :

```powershell
.\build_mobile.ps1
git add sih_mobile mobile_dist
git commit -m "Update Flutter mobile"
git push
```
