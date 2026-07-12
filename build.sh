#!/usr/bin/env bash
set -o errexit

echo "==> Installation Python"
pip install -r requirements.txt

echo "==> Build frontend Vue (sih-frontend)"
cd sih-frontend
npm install
npm run build
cd ..

echo "==> Migrations Django"
python manage.py migrate --noinput

echo "==> Fichiers statiques Django (admin)"
python manage.py collectstatic --noinput

echo "==> Build terminé"
