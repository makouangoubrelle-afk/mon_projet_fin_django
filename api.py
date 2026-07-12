from typing import Optional
from ninja import NinjaAPI, Schema
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import random
import re
import string
from laboratory.api import lab_router
from admission.api import admission_router
from consultation.api import consultation_router
from clinical.api import clinical_router
from pharmacy.api import pharmacy_router
from billing.api import billing_router
from users.api import personnel_router
from core.api import core_router

api = NinjaAPI(
    title="SGHL — Système de Gestion Hospitalière et de Laboratoire",
    version="1.0.0",
    description="ERP Médical Intégré — API REST",
)

ROLE_LABELS = {
    'ADMIN': 'Administrateur',
    'SECRETAIRE_GENERALE': 'Secrétaire générale',
    'MEDECIN': 'Médecin',
    'INFIRMIER': 'Infirmier',
    'SECRETAIRE': 'Secrétaire',
    'RECEPTIONNISTE': 'Réceptionniste',
    'BIOLOGISTE': 'Biologiste / Laborantin',
    'PHARMACIEN': 'Pharmacien',
    'PATIENT': 'Patient',
}

FULL_ACCESS_ROLES = {'ADMIN'}
STAFF_WIDE_ROLES = {'ADMIN', 'SECRETAIRE_GENERALE'}

OTP_VALIDITY_MINUTES = getattr(settings, 'OTP_VALIDITY_MINUTES', 10)


class EmailSchema(Schema):
    email: str


class SendCodeSchema(Schema):
    email: str
    channel: str = 'email'  # email | sms
    phone: str = ''
    role: str = ''


class VerifyCodeSchema(Schema):
    email: str
    code: str
    role: str = ''
    phone: str = ''


class AuthResponseSchema(Schema):
    success: bool
    username: str = ''
    email: str = ''
    role: str = ''
    role_label: str = ''
    token: str = ''
    patient_id: Optional[int] = None
    service_id: Optional[int] = None
    user_id: Optional[int] = None
    can_access_all: bool = False
    can_manage_ui: bool = False
    message: str = ''
    detail: str = ''


def _auth_token(user) -> str:
    import hashlib
    raw = f"{user.id}:{user.username}:{user.role}:{timezone.now().isoformat()}:{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()[:48]


def _user_auth_payload(user) -> dict:
    from admission.models import Patient
    payload = {
        'success': True,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'role_label': ROLE_LABELS.get(user.role, user.role),
        'token': _auth_token(user),
        'service_id': user.service_id,
        'user_id': user.id,
        'message': 'Connexion réussie',
        'patient_id': None,
    }
    dossier = Patient.objects.filter(user=user).first()
    if not dossier and user.role == 'PATIENT' and user.email:
        from admission.api import ensure_patient_portal, _resolve_patient_by_email
        dossier = _resolve_patient_by_email(user.email)
        if dossier:
            ensure_patient_portal(dossier, user.email)
            dossier.refresh_from_db()
    if not dossier and user.role == 'PATIENT' and user.email:
        dossier = Patient.objects.filter(email__iexact=user.email).first()
        if dossier and not dossier.user_id:
            dossier.user = user
            dossier.save(update_fields=['user'])
    if dossier:
        payload['patient_id'] = dossier.id
    payload['can_access_all'] = user.role in FULL_ACCESS_ROLES
    payload['can_manage_ui'] = user.role in FULL_ACCESS_ROLES
    payload['can_manage_redirects'] = user.role in FULL_ACCESS_ROLES
    if user.role == 'MEDECIN':
        try:
            doc = user.profil_medecin
            payload['medecin_service_ids'] = list(doc.services.values_list('id', flat=True))
            if doc.service_id and doc.service_id not in payload['medecin_service_ids']:
                payload['medecin_service_ids'].append(doc.service_id)
        except Exception:
            payload['medecin_service_ids'] = [user.service_id] if user.service_id else []
    return payload


def _generate_otp_code() -> str:
    return ''.join(random.choices(string.digits, k=6))


def _normalize_email(email: str) -> str:
    import re
    raw = (email or '').strip().lower()
    match = re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', raw, re.I)
    return match.group(0).lower() if match else raw


def _normalize_login_identifier(raw_input: str) -> str:
    """Accepte email complet ou identifiant seul → email par défaut @sghl.com."""
    text = (raw_input or '').strip().lower()
    if not text:
        return text
    if '@' in text:
        return _normalize_email(text)
    local = re.sub(r'[^a-z0-9._-]', '', text.replace(' ', '.'))
    domain = getattr(settings, 'DEFAULT_EMAIL_DOMAIN', 'sghl.com')
    return f'{local}@{domain}'


def _ensure_patient_user(email: str):
    """Crée ou retrouve un compte PATIENT si un dossier existe avec cet email."""
    from users.models import User
    from admission.models import Patient
    from admission.api import ensure_patient_portal

    user = User.objects.filter(email__iexact=email).first()
    if user:
        return user

    patient = Patient.objects.filter(email__iexact=email).first()
    if not patient:
        return None

    ensure_patient_portal(patient, email)
    return User.objects.filter(email__iexact=email).first()


def _match_patients_from_local(local: str):
    from admission.api import _match_patients_by_local
    return _match_patients_by_local(local)


def _gmail_local_part(raw: str) -> str:
    local = (raw or '').split('@')[0].lower()
    return re.sub(r'[^a-z0-9]', '', local)


def _find_user_by_gmail_hint(gmail: str, role: str = ''):
    """Associe un Gmail personnel à un compte existant (ex: makouangoubrelle → makouangourelle)."""
    from users.models import User

    local = _gmail_local_part(gmail)
    if len(local) < 4:
        return None

    qs = User.objects.filter(is_active=True)
    if role:
        qs = qs.filter(role=role.upper())

    best = None
    best_score = 0
    for user in qs:
        candidates = [user.email, user.username]
        if user.first_name:
            candidates.append(f'{user.first_name}{user.last_name}')
        for raw in candidates:
            cand = _gmail_local_part(raw.split('@')[0] if '@' in raw else raw)
            if not cand:
                continue
            # Score : préfixe commun le plus long
            common = 0
            for a, b in zip(local, cand):
                if a == b:
                    common += 1
                else:
                    break
            if local in cand or cand in local:
                common = max(common, min(len(local), len(cand)) - 1)
            if common >= 6 and common > best_score:
                best = user
                best_score = common
    return best


def _is_personal_email(email: str) -> bool:
    domain = email.split('@')[-1].lower() if '@' in email else ''
    return domain not in ('sghl.com', 'patient.sghl.com', '')


def _resolve_login_user(raw_input: str, phone: str = '', role: str = ''):
    """
    Retrouve un compte pour la connexion OTP.
    Retourne (user, email_pour_otp, message_erreur_ou_hint).
    """
    from users.models import User
    from admission.models import Patient
    from admission.api import ensure_patient_portal
    from users.otp_services import find_user_by_phone

    raw = (raw_input or '').strip()
    email = _normalize_login_identifier(raw)
    if not email or '@' not in email:
        if phone:
            user = find_user_by_phone(phone)
            if user:
                return user, user.email, None
        return None, email, 'Adresse email ou identifiant invalide.'

    # 1. Compte utilisateur exact
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if user and (not role or user.role == role.upper()):
        otp_dest = email if _is_personal_email(email) else user.email
        return user, otp_dest, None

    # 1b. Gmail personnel + profil choisi → recherche floue
    if _is_personal_email(email) and role:
        user = _find_user_by_gmail_hint(email, role)
        if user:
            return user, email, None

    # 1c. Gmail personnel sans rôle → un seul compte correspondant
    if _is_personal_email(email) and not role:
        user = _find_user_by_gmail_hint(email, '')
        if user:
            return user, email, None

    # 2. Identifiant seul → username (medecin → medecin@sghl.com)
    local, _, domain = email.partition('@')
    domain = domain.lower()
    if domain == getattr(settings, 'DEFAULT_EMAIL_DOMAIN', 'sghl.com'):
        user = User.objects.filter(username__iexact=local, is_active=True).first()
        if user and (not role or user.role == role.upper()):
            from users.otp_services import ensure_user_default_email
            canonical = ensure_user_default_email(user)
            return user, canonical, None

    # 3. Dossier patient avec cet email
    user = _ensure_patient_user(email)
    if user:
        return user, user.email, None

    # 4. Alias @sghl.com → portail patient ou dossier unique
    if domain == 'sghl.com':
        portal_candidate = f'{local}@patient.sghl.com'
        user = User.objects.filter(email__iexact=portal_candidate, is_active=True).first()
        if user:
            return user, user.email, None

        patient = Patient.objects.filter(email__iexact=portal_candidate).first()
        if patient:
            canonical = ensure_patient_portal(patient, email)
            user = User.objects.filter(email__iexact=canonical, is_active=True).first()
            if user:
                return user, canonical, None

        matches = _match_patients_from_local(local)
        if len(matches) == 1:
            canonical = ensure_patient_portal(matches[0], email)
            user = User.objects.filter(email__iexact=canonical, is_active=True).first()
            if user:
                return user, canonical, None

        if len(matches) > 1:
            return None, email, (
                'Plusieurs dossiers patients correspondent. '
                'Précisez votre email complet ou le format prenom.nom.'
            )

    # 5. Dossier patient orphelin
    orphan = Patient.objects.filter(email__iexact=email).first()
    if orphan:
        canonical = ensure_patient_portal(orphan, email)
        user = User.objects.filter(email__iexact=canonical, is_active=True).first()
        if user:
            return user, canonical, None

    # 6. Fallback : téléphone lié au compte
    if phone:
        user = find_user_by_phone(phone)
        if user:
            return user, user.email, None

    # 7. Email personnel valide + profil choisi → OTP autorisé (compte créé à la vérification)
    if _is_personal_email(email) and role:
        return None, email, None

    return None, email, (
        'Email non reconnu. Choisissez votre profil (Admin, Médecin, Patient…) '
        'puis réessayez, ou utilisez l\'email enregistré à l\'hôpital.'
    )


def _normalize_otp_code(code: str) -> str:
    return ''.join(c for c in (code or '') if c.isdigit())


def _find_valid_otp(email: str, code: str):
    from users.models import OtpCode
    otp = (
        OtpCode.objects.filter(
            email__iexact=email,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now(),
        )
        .order_by('-created_at')
        .first()
    )
    if otp:
        return otp
    # Mode souple : code existant non utilisé (même expiré en développement)
    if settings.DEBUG:
        return (
            OtpCode.objects.filter(email__iexact=email, code=code, is_used=False)
            .order_by('-created_at')
            .first()
        )
    return None


def _ensure_user_for_login(email: str, role: str = 'PATIENT'):
    """Retrouve ou crée un compte après validation OTP."""
    from users.models import User

    email = _normalize_email(email)
    role = (role or 'PATIENT').upper()
    valid = {c[0] for c in User.CHOIX_ROLES}
    if role not in valid:
        role = 'PATIENT'

    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if user:
        if user.role != role:
            user.role = role
            user.save(update_fields=['role'])
        return user

    user, _, _ = _resolve_login_user(email, role=role)
    if user:
        if user.email.lower() != email.lower():
            from users.otp_services import link_personal_email
            link_personal_email(user, email)
            user.refresh_from_db()
        if user.role != role:
            user.role = role
            user.save(update_fields=['role'])
        return user

    username = re.sub(r'[^a-z0-9_]', '_', email.split('@')[0].lower())[:30] or 'user'
    base = username
    n = 1
    while User.objects.filter(username=username).exists():
        username = f'{base}{n}'
        n += 1

    user = User.objects.create_user(
        username=username,
        email=email,
        password=None,
        role=role,
    )
    user.set_unusable_password()
    user.save(update_fields=['password'])

    if role == 'PATIENT':
        from admission.models import Patient
        from admission.api import ensure_patient_portal, _next_sgl_id
        from datetime import date
        patient = Patient.objects.filter(email__iexact=email).first()
        if not patient:
            local = email.split('@')[0]
            parts = local.replace('.', ' ').replace('_', ' ').split()
            nom = parts[-1].title() if parts else 'Patient'
            prenom = parts[0].title() if len(parts) > 1 else 'Nouveau'
            patient = Patient.objects.create(
                sgl_id=_next_sgl_id(),
                nom=nom,
                prenom=prenom,
                email=email,
                user=user,
                telephone='',
                date_naissance=date(2000, 1, 1),
                genre='M',
            )
        elif not patient.user_id:
            patient.user = user
            patient.save(update_fields=['user'])
        ensure_patient_portal(patient, email)
        user.refresh_from_db()

    return user


def _link_phone_after_login(user, phone: str = ''):
    from users.otp_services import link_user_phone, normalize_phone
    phone = normalize_phone(phone or '')
    if user and phone:
        link_user_phone(user, phone)


def _send_otp_email(email: str, code: str, role_label: str, user=None) -> None:
    from users.otp_services import send_otp_email
    display = ''
    username = ''
    role_code = ''
    if user:
        username = user.username
        role_code = user.role
        display = (user.first_name or user.username or '').strip().title()
    send_otp_email(
        email, code, role_label,
        username=username,
        role_code=role_code,
        display_name=display,
    )


@api.get('/auth/config', tags=['Authentification'])
def auth_config(request):
    from users.login_defaults import ROLE_DEFAULT_PERSONAL_EMAILS, admin_otp_phone, default_email_for_role
    from users.otp_services import default_email_domain, email_is_live, mask_phone, sms_is_live
    live = email_is_live()
    smtp_user = getattr(settings, 'ADMIN_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '')
    admin_phone = admin_otp_phone()
    return {
        'default_email_domain': default_email_domain(),
        'default_from_email': settings.DEFAULT_FROM_EMAIL,
        'otp_validity_minutes': OTP_VALIDITY_MINUTES,
        'channels': ['email', 'sms'],
        'sms_enabled': True,
        'sms_live': sms_is_live(),
        'email_live': live,
        'email_smtp_user': smtp_user if live else '',
        'sms_backend': getattr(settings, 'SMS_BACKEND', 'console'),
        'admin_email': getattr(settings, 'ADMIN_EMAIL', ''),
        'admin_phone_masked': mask_phone(admin_phone) if admin_phone else '',
        'role_default_emails': ROLE_DEFAULT_PERSONAL_EMAILS,
        'hint': (
            'Un code à 6 chiffres sera envoyé par email ou SMS à chaque connexion.'
            if (live or sms_is_live())
            else 'Entrez votre email et votre numéro de téléphone pour recevoir le code.'
        ),
        'login_roles': [
            {
                'code': code,
                'label': label,
                'default_email': default_email_for_role(code),
            }
            for code, label in [
                ('ADMIN', 'Administrateur'),
                ('SECRETAIRE_GENERALE', 'Secrétaire générale'),
                ('MEDECIN', 'Médecin'),
                ('INFIRMIER', 'Infirmier'),
                ('SECRETAIRE', 'Secrétaire'),
                ('RECEPTIONNISTE', 'Réceptionniste'),
                ('PATIENT', 'Patient'),
            ]
        ],
    }


@api.get('/auth/lookup', tags=['Authentification'])
def auth_lookup_user(request, email: str, phone: str = '', role: str = ''):
    from users.models import User
    from users.otp_services import (
        default_email_for_username,
        ensure_user_default_email,
        mask_phone,
        resolve_user_phone,
    )

    normalized = _normalize_login_identifier(email)
    if not normalized or '@' not in normalized:
        return {'found': False, 'detail': 'Adresse email invalide.'}

    user, otp_email, _ = _resolve_login_user(email, phone, role)
    role_code = (role or (user.role if user else 'PATIENT')).upper()
    role_label = ROLE_LABELS.get(user.role if user else role_code, role_code)

    if user:
        canonical = ensure_user_default_email(user) if not user.email else user.email
        resolved_phone = resolve_user_phone(user)
        otp_channel = getattr(user, 'otp_channel', 'EMAIL') or 'EMAIL'
        if otp_channel == 'SMS' and resolved_phone:
            otp_hint = f'Code OTP par SMS au {mask_phone(resolved_phone)}'
        else:
            otp_hint = f'Code OTP par email à {otp_email or normalized}'
        return {
            'found': True,
            'email': otp_email or normalized,
            'canonical_email': canonical,
            'default_email': default_email_for_username(user.username),
            'role_label': ROLE_LABELS.get(user.role, user.role),
            'phone': resolved_phone,
            'phone_masked': mask_phone(resolved_phone) if resolved_phone else '',
            'has_phone': bool(resolved_phone),
            'otp_channel': otp_channel,
            'otp_hint': otp_hint,
            'can_send_code': True,
            'account_found': True,
        }

    from users.login_defaults import default_email_for_role
    suggested = default_email_for_role(role_code) if role_code else normalized

    return {
        'found': True,
        'email': normalized if normalized else suggested,
        'suggested_email': suggested,
        'role_label': role_label,
        'can_send_code': True,
        'account_found': False,
        'detail': f'Un compte sera créé avec {normalized or suggested} au premier code validé.',
    }


@api.get("/sante", tags=["Supervision"])
def verifier_sante_systeme(request):
    return {"status": "healthy", "api_version": "1.0.0", "systeme": "SGHL"}


@api.get("/stats", tags=["Supervision"])
def statistiques_dashboard(request):
    from admission.models import Patient
    from clinical.models import Admission, BanqueSang, LocalisationPatient
    from consultation.models import Consultation
    from billing.models import Facture
    from django.db.models import Sum

    return {
        "patients": Patient.objects.count(),
        "hospitalises": Admission.objects.filter(est_cloture=False).count(),
        "consultations": Consultation.objects.count(),
        "patients_presents": LocalisationPatient.objects.exclude(statut='SORTI').count(),
        "factures_en_attente": Facture.objects.filter(statut='EN_ATTENTE').count(),
        "poches_sang": BanqueSang.objects.filter(statut='DISPONIBLE').count(),
        "revenus": float(
            Facture.objects.filter(statut='PAYE').aggregate(s=Sum('montant_patient_net'))['s'] or 0
        ),
    }


@api.get("/auth/comptes-demo", tags=["Authentification"])
def comptes_demo(request):
    return {
        "comptes": [
            {"email": "admin@sghl.com", "role": "Administrateur — accès total"},
            {"email": "secgenerale@sghl.com", "role": "Secrétaire générale — toutes les pages"},
            {"email": "medecin@sghl.com", "role": "Médecin — multi-services"},
            {"email": "infirmier@sghl.com", "role": "Infirmier"},
            {"email": "secretaire@sghl.com", "role": "Secrétaire — Cardiologie"},
            {"email": "secretaire.pedia@sghl.com", "role": "Secrétaire — Pédiatrie"},
            {"email": "patient@sghl.com", "role": "Patient — Mukendi Joseph"},
            {"email": "alaoui.anas@patient.sghl.com", "role": "Patient — alaoui anas"},
            {"email": "fatima.demo@patient.sghl.com", "role": "Patient — FATIMA DEMO"},
            {"email": "imane.rochdi@patient.sghl.com", "role": "Patient — imane rochdi"},
        ],
        "note": "Entrez votre email — un code à 6 chiffres vous sera envoyé automatiquement.",
    }


@api.post("/auth/quick-login", tags=["Authentification"])
def quick_login_dev(request, data: EmailSchema):
    """Connexion directe en mode développement (démo / tests UI)."""
    from users.models import User
    if not settings.DEBUG:
        return {"success": False, "detail": "Connexion rapide désactivée hors mode développement."}

    email = _normalize_email(data.email)
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return {
            "success": False,
            "detail": "Aucun compte pour cet email. Lancez : python manage.py seed_hospital",
        }
    return _user_auth_payload(user)


@api.get("/auth/health", tags=["Authentification"])
def auth_health(request):
    from users.models import User
    return {
        "ok": True,
        "debug": settings.DEBUG,
        "users": User.objects.count(),
    }


@api.post("/auth/send-code", tags=["Authentification"])
@transaction.atomic
def send_login_code(request, data: SendCodeSchema):
    from users.models import OtpCode, User
    from users.otp_services import (
        email_is_live,
        ensure_user_default_email,
        link_user_phone,
        mask_phone,
        normalize_phone,
        resolve_user_phone,
        send_otp_email,
        send_otp_sms,
        sms_is_live,
    )

    provided_email = _normalize_login_identifier(data.email)
    if not provided_email or '@' not in provided_email:
        return {'success': False, 'detail': 'Adresse email invalide.'}

    user, otp_email, _ = _resolve_login_user(data.email, data.phone or '', data.role or '')

    if provided_email and _is_personal_email(provided_email):
        email = provided_email
    elif user:
        if provided_email and provided_email != user.email and '@' in provided_email:
            from users.otp_services import link_personal_email
            email = link_personal_email(user, provided_email)
        else:
            email = otp_email or user.email or ensure_user_default_email(user)
    else:
        email = provided_email

    phone = normalize_phone(data.phone or '')
    if not phone and user:
        phone = resolve_user_phone(user)

    role = (data.role or (user.role if user else 'PATIENT')).upper()
    channel_pref = (data.channel or 'email').lower()

    # Canal OTP : admin = toujours par email ; autres = config du compte
    if role == 'ADMIN' or (user and user.role == 'ADMIN'):
        channel_pref = 'email'
    elif user:
        otp_channel = (getattr(user, 'otp_channel', 'EMAIL') or 'EMAIL').upper()
        if otp_channel == 'SMS' and phone:
            channel_pref = 'sms'
        else:
            channel_pref = 'email'

    if user and phone:
        link_user_phone(user, phone)

    role_label = ROLE_LABELS.get(user.role if user else role, ROLE_LABELS.get(role, role))

    OtpCode.objects.filter(email__iexact=email, is_used=False).update(is_used=True)

    code = _generate_otp_code()
    expires_at = timezone.now() + timedelta(minutes=OTP_VALIDITY_MINUTES)
    OtpCode.objects.create(
        email=email,
        code=code,
        channel='SMS' if channel_pref == 'sms' else 'EMAIL',
        phone=phone,
        expires_at=expires_at,
    )

    uname = user.username if user else email.split('@')[0]
    rcode = user.role if user else role
    display = (user.first_name if user and user.first_name else email.split('@')[0]).title()

    email_sent = False
    sms_sent = False
    email_error = None
    sms_error = None

    if channel_pref == 'sms' and phone and sms_is_live():
        try:
            send_otp_sms(phone, code, role_label)
            sms_sent = True
        except Exception as exc:
            sms_error = str(exc)
    else:
        try:
            send_otp_email(
                email, code, role_label,
                username=uname,
                role_code=rcode,
                display_name=display,
            )
            email_sent = True
        except Exception as exc:
            email_error = str(exc)

    email_live = email_is_live()
    sms_live = sms_is_live()
    delivery_live = (email_sent and email_live) or (sms_sent and sms_live)

    if email_live and not email_sent and not (sms_live and sms_sent):
        return {
            'success': False,
            'detail': (
                'Impossible d\'envoyer l\'email. Vérifiez EMAIL_HOST_PASSWORD dans .env '
                '(mot de passe d\'application Gmail).'
            ),
            'email': email,
            'delivery_live': True,
            'delivery_error': email_error,
        }

    if sms_live and phone and not sms_sent and not email_sent:
        return {
            'success': False,
            'detail': f'Impossible d\'envoyer le SMS au {mask_phone(phone)}. {sms_error or ""}'.strip(),
            'email': email,
            'phone_masked': mask_phone(phone),
            'delivery_live': True,
            'delivery_error': sms_error,
        }

    if delivery_live:
        if sms_sent and email_sent:
            detail = (
                f'Code envoyé par email à {email} et par SMS au {mask_phone(phone)}. '
                'Consultez votre téléphone.'
            )
            sent_via = 'both'
        elif sms_sent:
            detail = f'Code envoyé par SMS au {mask_phone(phone)}. Consultez votre téléphone.'
            sent_via = 'sms'
        else:
            detail = f'Code envoyé à {email}. Ouvrez votre application Mail sur votre téléphone.'
            sent_via = 'email'
    else:
        detail = 'Code généré (configurez Gmail ou SMS pour recevoir sur votre téléphone).'
        sent_via = 'dev'

    response = {
        'success': True,
        'detail': detail,
        'email': email,
        'phone_masked': mask_phone(phone) if phone else '',
        'channel': sent_via,
        'role_label': role_label,
        'expires_in_minutes': OTP_VALIDITY_MINUTES,
        'delivery_live': delivery_live,
        'account_found': bool(user),
    }
    if email_error and not email_sent:
        response['email_warning'] = email_error
    if sms_error and not sms_sent:
        response['sms_warning'] = sms_error
        if email_sent and not sms_sent:
            response['detail'] = (
                f'SMS indisponible ({sms_error}). '
                f'Code envoyé par email à {email}.' + (
                    '' if delivery_live else ' (mode développement — voir code à l\'écran).'
                )
            )
    if not delivery_live:
        response['debug_code'] = code
    return response


@api.post("/auth/verify-code", tags=["Authentification"])
def verify_login_code(request, data: VerifyCodeSchema):
    from users.models import User

    email = _normalize_email(data.email)
    code = _normalize_otp_code(data.code)

    if len(code) != 6:
        return {"success": False, "detail": "Le code doit contenir exactement 6 chiffres."}

    otp = _find_valid_otp(email, code)

    if not otp:
        user_hint, otp_email, _ = _resolve_login_user(data.email, role=data.role or '')
        if otp_email and otp_email != email:
            otp = _find_valid_otp(otp_email, code)
            if otp:
                email = otp_email

    if not otp and user_hint:
        otp = _find_valid_otp(user_hint.email, code)
        if otp:
            email = user_hint.email

    if not otp:
        return {
            'success': False,
            'detail': 'Code incorrect ou déjà utilisé. Demandez un nouveau code.',
        }

    otp.is_used = True
    otp.save(update_fields=['is_used'])

    user = _ensure_user_for_login(email, data.role or '')
    if not user:
        user = _ensure_user_for_login(data.email, data.role or '')

    _link_phone_after_login(user, data.phone or (otp.phone if otp else ''))

    from core.services import record_login, log_activity
    record_login(user, request, success=True)
    log_activity(request, 'Connexion réussie', 'Authentification', user.email, user=user)

    return _user_auth_payload(user)


@api.post("/auth/resend-code", tags=["Authentification"])
def resend_login_code(request, data: SendCodeSchema):
    """Renvoie un nouveau code (invalide l'ancien automatiquement)."""
    return send_login_code(request, data)


api.add_router("/reception", admission_router)
api.add_router("/consultations", consultation_router)
api.add_router("/hospitalisations", clinical_router)
api.add_router("/pharmacie", pharmacy_router)
api.add_router("/caisse", billing_router)
api.add_router("/labo", lab_router)
api.add_router("/personnel", personnel_router)
api.add_router("/core", core_router)
