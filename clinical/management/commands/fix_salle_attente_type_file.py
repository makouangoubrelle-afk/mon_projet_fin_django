import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ajoute la colonne type_file à clinical_salleattente si elle manque (file VIP)."

    def handle(self, *args, **options):
        db_path = str(settings.DATABASES['default']['NAME'])
        self.stdout.write(f'Base : {db_path}')
        conn = sqlite3.connect(db_path)
        cols = [r[1] for r in conn.execute('PRAGMA table_info(clinical_salleattente)').fetchall()]
        if 'type_file' in cols:
            self.stdout.write(self.style.SUCCESS('Colonne type_file déjà présente.'))
            conn.close()
            return
        conn.execute(
            "ALTER TABLE clinical_salleattente "
            "ADD COLUMN type_file varchar(15) NOT NULL DEFAULT 'STANDARD'"
        )
        conn.commit()
        row = conn.execute(
            "SELECT 1 FROM django_migrations WHERE app='clinical' AND name='0006_salleattente_type_file'"
        ).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO django_migrations (app, name, applied) "
                "VALUES ('clinical', '0006_salleattente_type_file', datetime('now'))"
            )
            conn.commit()
        conn.close()
        self.stdout.write(self.style.SUCCESS('Colonne type_file ajoutée avec succès.'))
