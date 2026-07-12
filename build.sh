#!/usr/bin/env bash
set -o errexit

echo "==> Installation Python"
pip install -r requirements.txt

echo "==> Build frontend Vue (sih-frontend)"
cd sih-frontend
npm install
npm run build
cd ..

echo "==> Build mobile Flutter (sih_mobile) si disponible"
if command -v flutter >/dev/null 2>&1; then
  cd sih_mobile
  flutter pub get
  rm -rf ../mobile_dist
  flutter build web --release --base-href /mobile/ --output ../mobile_dist
  cd ..
else
  echo "Flutter absent — utilisation de mobile_dist/ déjà compilé"
fi

echo "==> Migrations Django"
python manage.py migrate --noinput

echo "==> Fichiers statiques Django (admin)"
python manage.py collectstatic --noinput

echo "==> Build terminé"
