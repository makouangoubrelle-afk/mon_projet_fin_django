"""Emails personnels par défaut liés aux rôles SGHL."""

from django.conf import settings

# Emails Gmail suggérés à la connexion (créés en base au premier OTP validé)
ROLE_DEFAULT_PERSONAL_EMAILS = {
    'ADMIN': 'makouangoubrelle@gmail.com',
    'SECRETAIRE_GENERALE': 'secgenerale@gmail.com',
    'MEDECIN': 'medecin@gmail.com',
    'INFIRMIER': 'infirmier@gmail.com',
    'SECRETAIRE': 'secretaire@gmail.com',
    'RECEPTIONNISTE': 'reception@gmail.com',
    'PATIENT': 'patient@gmail.com',
}

# Comptes à pré-créer / lier en base (seed)
PERSONAL_LOGIN_ACCOUNTS = [
    {
        'role': 'ADMIN',
        'email': 'makouangoubrelle@gmail.com',
        'username': 'admin',
        'first_name': 'Admin',
        'last_name': 'SGHL',
        'phone_env': 'ADMIN_OTP_PHONE',
        'phone_default': '+24206900100',
        'otp_channel': 'EMAIL',
    },
    {
        'role': 'MEDECIN',
        'email': 'medecin@gmail.com',
        'username': 'medecin',
        'first_name': 'Dr. Jean',
        'last_name': 'Kabongo',
        'phone_default': '+24206900102',
    },
    {
        'role': 'INFIRMIER',
        'email': 'infirmier@gmail.com',
        'username': 'infirmier',
        'first_name': 'Marie',
        'last_name': 'Mputu',
        'phone_default': '+24206900103',
    },
    {
        'role': 'SECRETAIRE',
        'email': 'secretaire@gmail.com',
        'username': 'secretaire',
        'first_name': 'Grace',
        'last_name': 'Ilunga',
        'phone_default': '+24206900104',
    },
    {
        'role': 'RECEPTIONNISTE',
        'email': 'reception@gmail.com',
        'username': 'reception',
        'first_name': 'Paul',
        'last_name': 'Tshibanda',
        'phone_default': '+24206900106',
    },
    {
        'role': 'PATIENT',
        'email': 'patient@gmail.com',
        'username': 'patient',
        'first_name': 'Patient',
        'last_name': 'Demo',
        'phone_default': '+24206900200',
    },
]


def default_email_for_role(role: str) -> str:
    role = (role or 'PATIENT').upper()
    if role == 'ADMIN':
        try:
            from core.models import HospitalSettings
            hs = HospitalSettings.load()
            if hs.admin_otp_email:
                return hs.admin_otp_email.strip().lower()
        except Exception:
            pass
        return getattr(settings, 'ADMIN_EMAIL', ROLE_DEFAULT_PERSONAL_EMAILS['ADMIN'])
    return ROLE_DEFAULT_PERSONAL_EMAILS.get(role, '')


def admin_otp_phone() -> str:
    return getattr(settings, 'ADMIN_OTP_PHONE', '') or ''
