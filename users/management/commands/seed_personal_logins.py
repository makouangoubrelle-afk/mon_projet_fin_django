"""Crée ou met à jour les comptes avec emails personnels Gmail liés aux rôles."""

import os
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from users.login_defaults import PERSONAL_LOGIN_ACCOUNTS
from users.otp_services import link_user_phone, normalize_phone


class Command(BaseCommand):
    help = 'Lie les emails personnels (medecin@gmail.com, etc.) aux comptes SGHL'

    def _link_patient_dossier(self, user, email: str):
        from admission.models import Patient
        from admission.api import ensure_patient_portal, _next_sgl_id

        patient = Patient.objects.filter(user=user).first()
        if not patient:
            patient = Patient.objects.filter(email__iexact=email).first()
        if not patient:
            patient = (
                Patient.objects.filter(email__iexact='patient@sghl.com').first()
                or Patient.objects.filter(nom__iexact='Demo', prenom__iexact='Patient').first()
            )
        if not patient:
            patient = Patient.objects.create(
                sgl_id=_next_sgl_id(),
                nom='Demo',
                prenom='Patient',
                email=email,
                user=user,
                telephone='+24206900200',
                date_naissance=date(1990, 5, 15),
                genre='M',
                groupe_sanguin='O+',
            )
            self.stdout.write(self.style.SUCCESS(f'  Dossier patient créé pour {email}'))
        else:
            ensure_patient_portal(patient, email)
            patient.refresh_from_db()
            if patient.user_id != user.id:
                patient.user = user
                patient.save(update_fields=['user'])
            self.stdout.write(self.style.SUCCESS(f'  Dossier patient lié : {patient.nom} {patient.prenom}'))

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
            else:
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

            if role == 'PATIENT':
                self._link_patient_dossier(user, email)

        self.stdout.write(self.style.SUCCESS('Comptes personnels prêts pour la connexion OTP.'))
