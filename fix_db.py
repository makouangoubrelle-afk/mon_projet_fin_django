"""Fix inconsistent SQLite schema — reset clinical migrations safely."""
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parent / 'db.sqlite3'
if not db.exists():
    print('No db.sqlite3 found')
    raise SystemExit(0)

conn = sqlite3.connect(db)
cur = conn.cursor()
try:
    cur.execute('UPDATE users_user SET service_id = NULL')
    print('Cleared users.service_id references')
except sqlite3.OperationalError as e:
    print(f'Skip users update: {e}')

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'clinical_%'")
for (t,) in cur.fetchall():
    cur.execute(f'DROP TABLE IF EXISTS {t}')
    print(f'Dropped {t}')

cur.execute("DELETE FROM django_migrations WHERE app='clinical'")
cur.execute("DELETE FROM django_migrations WHERE app='users' AND name='0002_user_service_user_telephone_alter_user_role'")
conn.commit()
conn.close()
print('Done. Run: python manage.py migrate')
