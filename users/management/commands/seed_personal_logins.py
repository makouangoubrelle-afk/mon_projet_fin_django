"""Crée ou met à jour les comptes avec emails personnels Gmail liés aux rôles."""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from users.login_defaults import PERSONAL_LOGIN_ACCOUNTS
from users.otp_services import link_user_phone, normalize_phone


class Command(BaseCommand):
    help = 'Lie les emails personnels (medecin@gmail.com, etc.) aux comptes SGHL'

    def handle(self, *args, **options):
        User = get_user_model()
        for spec in PERSONAL_LOGIN_ACCOUNTS:
            role = spec['role']
            email = spec['email'].strip().lower()
            username = spec['username']
            phone = os.environ.get(spec.get('phone_env', ''), '').strip()
            if not phone:
                phone = spec.get('phone_default', '')

            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if not user:
                user = User.objects.filter(username__iexact=username, is_active=True).first()

            if user:
                user.email = email
                user.role = role
                user.first_name = spec.get('first_name', user.first_name)
                user.last_name = spec.get('last_name', user.last_name)
                user.otp_channel = spec.get('otp_channel', 'EMAIL')
                user.is_active = True
                user.save()
                if phone:
                    link_user_phone(user, phone)
                self.stdout.write(self.style.SUCCESS(f'Mis à jour : {email} ({role})'))
                continue

            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,
                role=role,
                first_name=spec.get('first_name', ''),
                last_name=spec.get('last_name', ''),
                otp_channel=spec.get('otp_channel', 'EMAIL'),
            )
            user.set_unusable_password()
            user.save(update_fields=['password'])
            if phone:
                link_user_phone(user, phone)
            self.stdout.write(self.style.SUCCESS(f'Créé : {email} ({role})'))

        self.stdout.write(self.style.SUCCESS('Comptes personnels prêts pour la connexion OTP.'))
