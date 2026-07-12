import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models as dj_models
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.errors import HttpError

from config.auth_helpers import get_api_user, require_admin
from config.serializers import iso
from .models import HospitalSettings, LoginHistory, ActivityLog, Notification
from .services import log_activity

User = get_user_model()
core_router = Router()


# --- Schémas ---

class HospitalSettingsSchema(Schema):
    nom_hopital: str
    adresse: str
    telephone: str
    email: str
    site_web: str = ''
    logo_url: str = ''
    devise: str = 'CDF'
    fuseau_horaire: str = 'Africa/Brazzaville'
    horaires_ouverture: str = ''
    directeur: str = ''
    siret: str = ''
    nom_application: str = 'SGHL'
    slogan_application: str = ''
    icone_application: str = '🏥'
    theme_ui: str = 'teal'
    config_style: dict = {}
    updated_at: str = ''


class HospitalSettingsUpdateSchema(Schema):
    nom_hopital: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    site_web: Optional[str] = None
    logo_url: Optional[str] = None
    devise: Optional[str] = None
    fuseau_horaire: Optional[str] = None
    horaires_ouverture: Optional[str] = None
    directeur: Optional[str] = None
    siret: Optional[str] = None
    nom_application: Optional[str] = None
    slogan_application: Optional[str] = None
    icone_application: Optional[str] = None
    theme_ui: Optional[str] = None
    config_style: Optional[dict] = None


class LoginHistorySchema(Schema):
    id: int
    email: str
    role: str
    ip_address: Optional[str] = None
    success: bool
    created_at: str


class ActivityLogSchema(Schema):
    id: int
    email: str
    role: str
    action: str
    module: str
    detail: str
    created_at: str


class NotificationSchema(Schema):
    id: int
    title: str
    message: str
    level: str
    is_read: bool
    link: str
    created_at: str
    is_global: bool = False


class NotificationCreateSchema(Schema):
    title: str
    message: str
    level: str = 'INFO'
    link: str = ''
    user_email: Optional[str] = None


class UserOutSchema(Schema):
    id: int
    username: str
    email: str
    role: str
    role_label: str
    telephone: str
    otp_channel: str = 'EMAIL'
    otp_channel_label: str = 'Email'
    service_id: Optional[int] = None
    service_nom: Optional[str] = None
    is_active: bool
    en_pause: bool
    is_primary_admin: bool = False
    last_login: Optional[str] = None
    date_joined: str


class UserCreateSchema(Schema):
    email: str
    username: str = ''
    role: str
    telephone: str = ''
    otp_channel: str = 'EMAIL'
    service_id: Optional[int] = None
    password: str = 'sghl123'


class UserUpdateSchema(Schema):
    email: Optional[str] = None
    role: Optional[str] = None
    telephone: Optional[str] = None
    otp_channel: Optional[str] = None
    service_id: Optional[int] = None
    is_active: Optional[bool] = None
    en_pause: Optional[bool] = None


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


def _settings_out(s: HospitalSettings) -> dict:
    return {
        'nom_hopital': s.nom_hopital,
        'adresse': s.adresse,
        'telephone': s.telephone,
        'email': s.email,
        'site_web': s.site_web,
        'logo_url': s.logo_url,
        'devise': s.devise,
        'fuseau_horaire': s.fuseau_horaire,
        'horaires_ouverture': s.horaires_ouverture,
        'directeur': s.directeur,
        'siret': s.siret,
        'nom_application': s.nom_application,
        'slogan_application': s.slogan_application,
        'icone_application': s.icone_application,
        'theme_ui': s.theme_ui,
        'config_style': s.config_style or {},
        'updated_at': iso(s.updated_at),
    }


def _user_out(u: User) -> dict:
    hs = HospitalSettings.load()
    primary_email = (hs.admin_otp_email or '').strip().lower()
    otp_ch = getattr(u, 'otp_channel', 'EMAIL') or 'EMAIL'
    otp_labels = {'EMAIL': 'Email', 'SMS': 'SMS (téléphone)'}
    return {
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'role_label': ROLE_LABELS.get(u.role, u.role),
        'telephone': u.telephone or '',
        'otp_channel': otp_ch,
        'otp_channel_label': otp_labels.get(otp_ch, otp_ch),
        'service_id': u.service_id,
        'service_nom': u.service.nom if u.service else None,
        'is_active': u.is_active,
        'en_pause': u.en_pause,
        'is_primary_admin': bool(primary_email and u.email.lower() == primary_email and u.role == 'ADMIN'),
        'last_login': iso(u.last_login) if u.last_login else None,
        'date_joined': iso(u.date_joined),
    }


# --- Paramètres hôpital ---

@core_router.get('/settings', response=HospitalSettingsSchema, tags=['Paramètres hôpital'])
def get_hospital_settings(request):
    return _settings_out(HospitalSettings.load())


@core_router.patch('/settings', response=HospitalSettingsSchema, tags=['Paramètres hôpital'])
def update_hospital_settings(request, data: HospitalSettingsUpdateSchema):
    require_admin(request)
    s = HospitalSettings.load()
    for field, value in data.dict(exclude_unset=True).items():
        setattr(s, field, value)
    s.save()
    log_activity(request, 'Modification paramètres hôpital', 'Paramètres', s.nom_hopital)
    return _settings_out(s)


# --- Historique connexions ---

@core_router.get('/login-history', response=List[LoginHistorySchema], tags=['Sécurité'])
def list_login_history(request, limit: int = 100):
    user = get_api_user(request)
    if not user or user.role not in ('ADMIN', 'SECRETAIRE_GENERALE'):
        raise HttpError(403, 'Accès réservé aux administrateurs.')
    qs = LoginHistory.objects.all().order_by('-created_at')[:min(limit, 500)]
    return [
        {
            'id': h.id,
            'email': h.email,
            'role': h.role,
            'ip_address': h.ip_address,
            'success': h.success,
            'created_at': iso(h.created_at),
        }
        for h in qs
    ]


# --- Journal activité ---

@core_router.get('/activity-log', response=List[ActivityLogSchema], tags=['Sécurité'])
def list_activity_log(request, limit: int = 100, module: str = ''):
    user = get_api_user(request)
    if not user or user.role not in ('ADMIN', 'SECRETAIRE_GENERALE'):
        raise HttpError(403, 'Accès réservé aux administrateurs.')
    qs = ActivityLog.objects.all()
    if module:
        qs = qs.filter(module__icontains=module)
    qs = qs.order_by('-created_at')[:min(limit, 500)]
    return [
        {
            'id': a.id,
            'email': a.email,
            'role': a.role,
            'action': a.action,
            'module': a.module,
            'detail': a.detail,
            'created_at': iso(a.created_at),
        }
        for a in qs
    ]


# --- Notifications ---

@core_router.get('/notifications', response=List[NotificationSchema], tags=['Notifications'])
def list_notifications(request, unread_only: bool = False):
    user = get_api_user(request)
    if not user:
        raise HttpError(401, 'Connexion requise.')
    from django.db.models import Q
    qs = Notification.objects.filter(Q(user=user) | Q(user__isnull=True))
    if unread_only:
        qs = qs.filter(is_read=False)
    return [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'level': n.level,
            'is_read': n.is_read,
            'link': n.link,
            'created_at': iso(n.created_at),
            'is_global': n.user_id is None,
        }
        for n in qs.order_by('-created_at')[:50]
    ]


@core_router.post('/notifications/{notif_id}/read', tags=['Notifications'])
def mark_notification_read(request, notif_id: int):
    user = get_api_user(request)
    if not user:
        raise HttpError(401, 'Connexion requise.')
    from django.db.models import Q
    n = get_object_or_404(Notification, Q(user=user) | Q(user__isnull=True), id=notif_id)
    n.is_read = True
    n.save(update_fields=['is_read'])
    return {'success': True}


@core_router.post('/notifications/read-all', tags=['Notifications'])
def mark_all_notifications_read(request):
    user = get_api_user(request)
    if not user:
        raise HttpError(401, 'Connexion requise.')
    from django.db.models import Q
    Notification.objects.filter(Q(user=user) | Q(user__isnull=True), is_read=False).update(is_read=True)
    return {'success': True}


@core_router.post('/notifications', response=NotificationSchema, tags=['Notifications'])
def create_notification(request, data: NotificationCreateSchema):
    require_admin(request)
    target = None
    if data.user_email:
        target = get_object_or_404(User, email__iexact=data.user_email.strip())
    n = Notification.objects.create(
        user=target,
        title=data.title,
        message=data.message,
        level=data.level if data.level in dict(Notification.LEVEL_CHOICES) else 'INFO',
        link=data.link or '',
    )
    log_activity(request, 'Notification créée', 'Notifications', data.title)
    return {
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'level': n.level,
        'is_read': n.is_read,
        'link': n.link,
        'created_at': iso(n.created_at),
        'is_global': n.user_id is None,
    }


# --- Gestion utilisateurs ---

@core_router.get('/users', response=List[UserOutSchema], tags=['Utilisateurs'])
def list_users(request, role: str = ''):
    require_admin(request)
    qs = User.objects.select_related('service').exclude(role='PATIENT').order_by('role', 'email')
    if role:
        qs = qs.filter(role=role.upper())
    return [_user_out(u) for u in qs]


@core_router.post('/users', response=UserOutSchema, tags=['Utilisateurs'])
def create_user(request, data: UserCreateSchema):
    require_admin(request)
    valid_roles = {c[0] for c in User.CHOIX_ROLES}
    if data.role not in valid_roles or data.role == 'PATIENT':
        raise HttpError(400, f'Rôle invalide. Choix : {", ".join(r for r in valid_roles if r != "PATIENT")}')
    email = data.email.strip().lower()
    if User.objects.filter(email__iexact=email).exists():
        raise HttpError(400, 'Cet email est déjà utilisé.')
    username = data.username.strip() or email.split('@')[0]
    base = username
    n = 1
    while User.objects.filter(username=username).exists():
        username = f'{base}{n}'
        n += 1
    u = User.objects.create_user(
        username=username,
        email=email,
        password=data.password,
        role=data.role,
        telephone=data.telephone or '',
        otp_channel=(data.otp_channel or 'EMAIL').upper(),
        service_id=data.service_id,
    )
    if data.telephone:
        from users.otp_services import link_user_phone
        link_user_phone(u, data.telephone)
        u.refresh_from_db()
    log_activity(request, 'Création utilisateur', 'Utilisateurs', f'{email} ({data.role})')
    return _user_out(u)


@core_router.patch('/users/{user_id}', response=UserOutSchema, tags=['Utilisateurs'])
def update_user(request, user_id: int, data: UserUpdateSchema):
    require_admin(request)
    u = get_object_or_404(User, id=user_id)
    if u.role == 'ADMIN' and data.is_active is False:
        raise HttpError(400, 'Impossible de désactiver le compte administrateur principal.')
    payload = data.dict(exclude_unset=True)
    for field, value in payload.items():
        if field == 'role' and value:
            valid = {c[0] for c in User.CHOIX_ROLES}
            if value not in valid:
                raise HttpError(400, 'Rôle invalide.')
        if field == 'otp_channel' and value:
            if value.upper() not in ('EMAIL', 'SMS'):
                raise HttpError(400, 'Canal OTP invalide (EMAIL ou SMS).')
            value = value.upper()
        setattr(u, field, value)
    u.save()
    if 'telephone' in payload and payload['telephone'] is not None:
        from users.otp_services import link_user_phone
        link_user_phone(u, payload['telephone'])
        u.refresh_from_db()
    log_activity(request, 'Modification utilisateur', 'Utilisateurs', u.email)
    return _user_out(u)


@core_router.get('/admin-otp', tags=['Utilisateurs'])
def get_admin_otp_config(request):
    require_admin(request)
    hs = HospitalSettings.load()
    primary_email = (hs.admin_otp_email or '').strip().lower()
    admin_user = None
    if primary_email:
        admin_user = User.objects.filter(email__iexact=primary_email, role='ADMIN').first()
    if not admin_user:
        admin_user = User.objects.filter(role='ADMIN', is_active=True).order_by('id').first()
    return {
        'admin_email': primary_email or (admin_user.email if admin_user else ''),
        'admin_user_id': admin_user.id if admin_user else None,
        'admin_user_label': admin_user.email if admin_user else '',
    }


@core_router.post('/users/{user_id}/set-primary-admin', response=UserOutSchema, tags=['Utilisateurs'])
def set_primary_admin(request, user_id: int):
    """Définit l'administrateur principal (connexion OTP + droits admin)."""
    require_admin(request)
    u = get_object_or_404(User, id=user_id)
    if u.role == 'PATIENT':
        raise HttpError(400, 'Un patient ne peut pas devenir administrateur.')
    if not u.telephone and (getattr(u, 'otp_channel', 'EMAIL') or 'EMAIL') == 'SMS':
        raise HttpError(400, 'Ajoutez un numéro de téléphone ou choisissez le canal Email.')

    u.role = 'ADMIN'
    u.is_active = True
    u.otp_channel = 'EMAIL'
    u.save(update_fields=['role', 'is_active', 'otp_channel'])

    hs = HospitalSettings.load()
    hs.admin_otp_email = u.email.strip().lower()
    hs.save(update_fields=['admin_otp_email'])

    log_activity(request, 'Changement administrateur principal', 'Utilisateurs', u.email)
    return _user_out(u)


@core_router.get('/roles', tags=['Utilisateurs'])
def list_roles(request):
    return {
        'roles': [
            {'code': code, 'label': ROLE_LABELS.get(code, label)}
            for code, label in User.CHOIX_ROLES
        ]
    }


# --- Rapports & statistiques ---

@core_router.get('/reports', tags=['Rapports'])
def rapports_complets(request):
    user = get_api_user(request)
    if not user or user.role not in ('ADMIN', 'SECRETAIRE_GENERALE', 'SECRETAIRE', 'RECEPTIONNISTE'):
        raise HttpError(403, 'Accès réservé au personnel autorisé.')

    from admission.models import Patient, RendezVous
    from clinical.models import Admission, BanqueSang, Lit
    from consultation.models import Consultation, Ordonnance
    from billing.models import Facture, Paiement
    from pharmacy.models import Medicament, PrescriptionPharmacie
    from users.models import Docteur, Infirmier

    meds_top = (
        PrescriptionPharmacie.objects
        .values('medicament__nom')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )
    chambres_occupees = Lit.objects.filter(est_occupe=True).count()
    chambres_total = Lit.objects.count()
    stock_pharmacie = Medicament.objects.aggregate(
        total=Sum('quantite_en_stock'),
        alertes=Count('id', filter=dj_models.Q(quantite_en_stock__lte=10)),
    )
    poches_sang = BanqueSang.objects.filter(statut='DISPONIBLE').count()
    revenus = float(Facture.objects.filter(statut='PAYE').aggregate(s=Sum('montant_patient_net'))['s'] or 0)
    depenses = float(
        Paiement.objects.filter(mode_paiement='VIREMENT').aggregate(s=Sum('montant'))['s'] or 0
    )

    return {
        'patients': Patient.objects.count(),
        'consultations': Consultation.objects.count(),
        'ordonnances': Ordonnance.objects.count(),
        'rendez_vous': RendezVous.objects.count(),
        'hospitalises': Admission.objects.filter(est_cloture=False).count(),
        'medecins': Docteur.objects.filter(est_actif=True).count(),
        'infirmiers': Infirmier.objects.filter(est_actif=True).count(),
        'factures_en_attente': Facture.objects.filter(statut='EN_ATTENTE').count(),
        'factures_payees': Facture.objects.filter(statut='PAYE').count(),
        'revenus': revenus,
        'depenses': depenses,
        'paiements_total': Paiement.objects.count(),
        'occupation_chambres': {
            'lits_occupes': chambres_occupees,
            'lits_total': chambres_total,
            'taux': round(chambres_occupees / chambres_total * 100, 1) if chambres_total else 0,
        },
        'stock_pharmacie': {
            'unites': int(stock_pharmacie['total'] or 0),
            'alertes_rupture': stock_pharmacie['alertes'] or 0,
            'medicaments_expires': Medicament.objects.filter(
                date_expiration__lt=datetime.now().date()
            ).count() if hasattr(Medicament, 'date_expiration') else 0,
        },
        'stock_sang': poches_sang,
        'medicaments_plus_utilises': [
            {'nom': m['medicament__nom'] or '—', 'quantite': m['total']}
            for m in meds_top
        ],
        'connexions_recentes': LoginHistory.objects.filter(success=True).count(),
        'activites_recentes': ActivityLog.objects.count(),
    }


# --- Sauvegarde ---

@core_router.post('/backup', tags=['Sauvegarde'])
def create_backup(request):
    require_admin(request)
    backup_dir = settings.BASE_DIR / 'backups'
    backup_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db = settings.DATABASES['default']
    engine = db.get('ENGINE', '')

    if 'postgresql' in engine:
        import subprocess
        dest = backup_dir / f'sghl_backup_{stamp}.sql'
        env = os.environ.copy()
        env['PGPASSWORD'] = str(db.get('PASSWORD', ''))
        try:
            subprocess.run(
                [
                    'pg_dump',
                    '-h', str(db.get('HOST', 'localhost')),
                    '-p', str(db.get('PORT', '5432')),
                    '-U', str(db.get('USER', 'postgres')),
                    '-d', str(db.get('NAME', 'sghl')),
                    '-f', str(dest),
                    '--no-owner',
                    '--no-acl',
                ],
                env=env,
                check=True,
                capture_output=True,
            )
        except FileNotFoundError:
            raise HttpError(
                500,
                'pg_dump introuvable. Installez PostgreSQL client tools ou sauvegardez depuis pgAdmin.',
            )
        except subprocess.CalledProcessError as exc:
            raise HttpError(500, f'Échec pg_dump : {exc.stderr.decode(errors="replace")[:500]}')
    else:
        db_path = Path(db['NAME'])
        if not db_path.exists():
            raise HttpError(500, 'Base de données introuvable.')
        dest = backup_dir / f'sghl_backup_{stamp}.sqlite3'
        shutil.copy2(db_path, dest)

    log_activity(request, 'Sauvegarde créée', 'Sauvegarde', dest.name)
    return {
        'success': True,
        'filename': dest.name,
        'path': str(dest),
        'size_bytes': dest.stat().st_size,
    }


@core_router.get('/backups', tags=['Sauvegarde'])
def list_backups(request):
    require_admin(request)
    backup_dir = settings.BASE_DIR / 'backups'
    if not backup_dir.exists():
        return {'backups': []}
    files = sorted(
        list(backup_dir.glob('sghl_backup_*.sql')) + list(backup_dir.glob('sghl_backup_*.sqlite3')),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    return {
        'backups': [
            {
                'filename': f.name,
                'size_bytes': f.stat().st_size,
                'created_at': datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            }
            for f in files[:20]
        ]
    }
