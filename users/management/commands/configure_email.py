"""Configure Gmail SMTP dans .env pour envoyer les codes OTP par email."""

import re
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Enregistre le mot de passe d\'application Gmail dans .env'

    def add_arguments(self, parser):
        parser.add_argument(
            'password',
            help='Mot de passe d\'application Gmail (16 caractères, espaces acceptés)',
        )
        parser.add_argument(
            '--email',
            default='makouangoubrelle@gmail.com',
            help='Adresse Gmail expéditrice',
        )

    def handle(self, *args, **options):
        password = re.sub(r'\s+', '', options['password'] or '')
        email = (options['email'] or '').strip().lower()

        if len(password) < 8:
            self.stderr.write(self.style.ERROR('Mot de passe trop court.'))
            return
        if '@' not in email:
            self.stderr.write(self.style.ERROR('Email invalide.'))
            return

        env_path = Path(__file__).resolve().parents[3] / '.env'
        if not env_path.exists():
            self.stderr.write(self.style.ERROR(f'Fichier introuvable : {env_path}'))
            return

        text = env_path.read_text(encoding='utf-8')
        text = re.sub(
            r'^EMAIL_HOST_USER=.*$',
            f'EMAIL_HOST_USER={email}',
            text,
            flags=re.MULTILINE,
        )
        text = re.sub(
            r'^EMAIL_HOST_PASSWORD=.*$',
            f'EMAIL_HOST_PASSWORD={password}',
            text,
            flags=re.MULTILINE,
        )
        if 'EMAIL_BACKEND=' not in text:
            text += (
                '\nEMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend\n'
                f'EMAIL_HOST_USER={email}\n'
                f'EMAIL_HOST_PASSWORD={password}\n'
            )
        env_path.write_text(text, encoding='utf-8')

        self.stdout.write(self.style.SUCCESS(
            f'Gmail configuré pour {email}.\n'
            'Redémarrez Django puis testez : python manage.py test_otp_email'
        ))
