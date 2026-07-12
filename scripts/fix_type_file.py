"""Ajoute type_file si la migration n'a pas été appliquée sur la base locale."""
import os
import sys
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings

db_path = str(settings.DATABASES['default']['NAME'])
print('Base:', db_path)

conn = sqlite3.connect(db_path)
cols = [r[1] for r in conn.execute('PRAGMA table_info(clinical_salleattente)').fetchall()]
print('Colonnes actuelles:', cols)

if 'type_file' not in cols:
    conn.execute(
        "ALTER TABLE clinical_salleattente ADD COLUMN type_file varchar(15) NOT NULL DEFAULT 'STANDARD'"
    )
    conn.commit()
    print('Colonne type_file ajoutée.')
else:
    print('Colonne type_file déjà présente.')

# Enregistrer la migration si absente
row = conn.execute(
    "SELECT 1 FROM django_migrations WHERE app='clinical' AND name='0006_salleattente_type_file'"
).fetchone()
if not row:
    conn.execute(
        "INSERT INTO django_migrations (app, name, applied) VALUES ('clinical', '0006_salleattente_type_file', datetime('now'))"
    )
    conn.commit()
    print('Migration 0006 enregistrée.')

conn.close()
print('OK')
