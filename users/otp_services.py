"""Envoi OTP par email ou SMS + adresses email par défaut SGHL."""
import re
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def default_email_domain() -> str:
    return getattr(settings, 'DEFAULT_EMAIL_DOMAIN', 'sghl.com')


def default_email_for_username(username: str) -> str:
    local = (username or '').strip().lower().replace(' ', '.')
    return f'{local}@{default_email_domain()}'


def ensure_user_default_email(user):
    """Attribue une adresse @sghl.com si le compte n'en a pas."""
    if user.email and '@' in user.email:
        return user.email
    generated = default_email_for_username(user.username)
    user.email = generated
    user.save(update_fields=['email'])
    return generated


def normalize_phone(raw: str) -> str:
    if not raw:
        return ''
    digits = re.sub(r'\D', '', raw)
    if digits.startswith('2420') and len(digits) >= 7:
        return f'+242{digits[4:]}'
    if digits.startswith('242') and len(digits) >= 6:
        return f'+{digits}'
    if digits.startswith('0') and len(digits) >= 8:
        return f'+242{digits[1:]}'
    if len(digits) >= 8:
        return f'+242{digits}'
    return raw.strip()


def mask_phone(phone: str) -> str:
    p = normalize_phone(phone)
    if len(p) < 6:
        return '***'
    return f'{p[:4]} *** ** {p[-2:]}'


def link_user_phone(user, phone: str) -> str:
    """Enregistre le téléphone sur le compte et propage vers les profils liés."""
    phone = normalize_phone(phone)
    if not phone or not user:
        return ''

    if user.telephone != phone:
        user.telephone = phone
        user.save(update_fields=['telephone'])

    if user.role == 'MEDECIN':
        try:
            profil = user.profil_medecin
            if profil.telephone != phone:
                profil.telephone = phone
                profil.save(update_fields=['telephone'])
        except Exception:
            pass
    elif user.role == 'INFIRMIER':
        try:
            profil = user.profil_infirmier
            if profil.telephone != phone:
                profil.telephone = phone
                profil.save(update_fields=['telephone'])
        except Exception:
            pass
    elif user.role == 'PATIENT':
        from admission.models import Patient
        patient = Patient.objects.filter(user=user).first()
        if not patient and user.email:
            patient = Patient.objects.filter(email__iexact=user.email).first()
        if patient and patient.telephone != phone:
            patient.telephone = phone
            patient.save(update_fields=['telephone'])

    return phone


def find_user_by_phone(phone: str):
    """Retrouve un compte actif à partir de son numéro (User ou dossier patient)."""
    from users.models import User

    normalized = normalize_phone(phone)
    if not normalized:
        return None

    digits_tail = normalized[-9:] if len(normalized) >= 9 else normalized

    for user in User.objects.filter(is_active=True).select_related():
        if normalize_phone(user.telephone) == normalized:
            return user
        if resolve_user_phone(user) == normalized:
            return user

    from admission.models import Patient
    patient = Patient.objects.filter(telephone__icontains=digits_tail).select_related('user').first()
    if patient:
        if patient.user_id and patient.user.is_active:
            return patient.user
        from admission.api import ensure_patient_portal
        canonical = ensure_patient_portal(patient, patient.email)
        return User.objects.filter(email__iexact=canonical, is_active=True).first()

    return None


def link_personal_email(user, raw_email: str) -> str:
    """Lie un email personnel au compte si disponible."""
    from users.models import User

    email = (raw_email or '').strip().lower()
    if not email or '@' not in email or email == user.email:
        return user.email
    if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
        return user.email
    user.email = email
    user.save(update_fields=['email'])
    return email


def resolve_user_phone(user) -> str:
    if not user:
        return ''
    if user.telephone:
        return normalize_phone(user.telephone)

    if user.role == 'PATIENT':
        from admission.models import Patient
        patient = Patient.objects.filter(user=user).first()
        if not patient and user.email:
            patient = Patient.objects.filter(email__iexact=user.email).first()
        if patient and patient.telephone:
            return normalize_phone(patient.telephone)

    if user.role == 'MEDECIN':
        try:
            if user.profil_medecin.telephone:
                return normalize_phone(user.profil_medecin.telephone)
        except Exception:
            pass

    if user.role == 'INFIRMIER':
        try:
            if user.profil_infirmier.telephone:
                return normalize_phone(user.profil_infirmier.telephone)
        except Exception:
            pass

    return ''


def sms_is_live() -> bool:
    """Vrai si un fournisseur SMS réel est configuré (le code part sur le téléphone)."""
    backend = getattr(settings, 'SMS_BACKEND', 'console')
    if backend == 'twilio':
        return bool(
            getattr(settings, 'TWILIO_ACCOUNT_SID', '')
            and getattr(settings, 'TWILIO_AUTH_TOKEN', '')
            and getattr(settings, 'TWILIO_FROM_NUMBER', '')
        )
    if backend == 'textbelt':
        # Textbelt fonctionne même sans clé ('textbelt' = 1 SMS gratuit/jour)
        return True
    return False


def email_is_live() -> bool:
    """Vrai si Gmail/SMTP est configuré avec identifiants valides."""
    backend = getattr(settings, 'EMAIL_BACKEND', '')
    user = getattr(settings, 'EMAIL_HOST_USER', '')
    password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    return 'smtp' in backend.lower() and bool(user) and bool(password)


def send_otp_email(
    email: str,
    code: str,
    role_label: str,
    *,
    username: str = '',
    role_code: str = '',
    display_name: str = '',
) -> None:
    from django.core.mail import EmailMultiAlternatives

    from users.email_templates import build_otp_email_html, build_otp_email_text

    validity = getattr(settings, 'OTP_VALIDITY_MINUTES', 10)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@sghl.com')
    subject = 'SGHL — Code de vérification'

    app_name = 'SGHL ERP MÉDICAL'
    hospital_name = 'CHU — Centre Hospitalier Universitaire'
    try:
        from core.models import HospitalSettings
        hs = HospitalSettings.objects.first()
        if hs:
            if hs.nom_application:
                app_name = hs.nom_application.upper()
            if hs.nom_hopital:
                hospital_name = hs.nom_hopital
    except Exception:
        pass

    text_body = build_otp_email_text(
        code=code,
        username=username or email.split('@')[0],
        role_label=role_label,
        role_code=role_code or role_label,
        display_name=display_name,
        validity_minutes=validity,
    )
    html_body = build_otp_email_html(
        code=code,
        username=username or email.split('@')[0],
        role_label=role_label,
        role_code=role_code or role_label,
        display_name=display_name,
        validity_minutes=validity,
        app_name=app_name,
        hospital_name=hospital_name,
    )

    msg = EmailMultiAlternatives(subject, text_body, from_email, [email])
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=False)

    if not email_is_live():
        logger.info('Email OTP -> %s : %s', email, code)
        print(f'\n[EMAIL SGHL] -> {email}\nCode : {code}\n')


def send_otp_sms(phone: str, code: str, role_label: str) -> str:
    """Envoie le code par SMS. Retourne le mode utilisé : 'twilio', 'textbelt' ou 'console'."""
    phone = normalize_phone(phone)
    if not phone:
        raise ValueError('Numéro de téléphone invalide.')

    body = f'SGHL ({role_label}) — Votre code : {code}. Valable 10 min.'
    backend = getattr(settings, 'SMS_BACKEND', 'console')

    if backend == 'twilio':
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=body,
            from_=settings.TWILIO_FROM_NUMBER,
            to=phone,
        )
        return 'twilio'

    if backend == 'textbelt':
        import json
        import urllib.request

        api_key = (getattr(settings, 'TEXTBELT_KEY', '') or 'textbelt').strip() or 'textbelt'
        payload = json.dumps({
            'phone': phone,
            'message': body,
            'key': api_key,
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://textbelt.com/text',
            data=payload,
            headers={'Content-Type': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        if not result.get('success'):
            raise ValueError(f"Envoi Textbelt refusé : {result.get('error', 'erreur inconnue')}")
        return 'textbelt'

    # Mode console / développement
    logger.info('SMS OTP -> %s : %s', phone, code)
    print(f'\n[SMS SGHL] -> {phone}\n{body}\n')
    return 'console'
