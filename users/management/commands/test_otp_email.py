"""Envoie un email OTP de test pour valider la configuration Gmail SMTP."""

from django.core.management.base import BaseCommand

from users.otp_services import email_is_live, send_otp_email


class Command(BaseCommand):
    help = 'Teste l\'envoi d\'un code OTP par email (Gmail SMTP)'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            nargs='?',
            default='makouangoubrelle@gmail.com',
            help='Adresse de destination (défaut: makouangoubrelle@gmail.com)',
        )

    def handle(self, *args, **options):
        dest = (options['email'] or '').strip()
        if not dest or '@' not in dest:
            self.stderr.write(self.style.ERROR('Adresse email invalide.'))
            return

        if not email_is_live():
            self.stderr.write(self.style.ERROR(
                'Email SMTP non configuré.\n'
                'Ouvrez .env et renseignez EMAIL_HOST_PASSWORD avec un mot de passe '
                'd\'application Gmail (https://myaccount.google.com/apppasswords).'
            ))
            return

        code = '123456'
        try:
            send_otp_email(
                dest,
                code,
                'Test administrateur',
                username='test',
                role_code='ADMIN',
                display_name='Test SGHL',
            )
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'Échec envoi : {exc}'))
            return

        self.stdout.write(self.style.SUCCESS(
            f'Email de test envoyé à {dest}. Consultez votre boîte mail (et les spams).'
        ))
