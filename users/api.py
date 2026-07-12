from ninja import Router, Schema
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from config.serializers import iso
from .models import Docteur, Infirmier

User = get_user_model()
personnel_router = Router()


class DocteurCreateSchema(Schema):
    nom: str
    prenom: str
    specialite: str
    email: str
    telephone: str
    adresse: str = ''
    numero_ordre: str = ''
    photo: str = ''
    service_id: Optional[int] = None
    service_ids: Optional[List[int]] = None


class DocteurUpdateSchema(Schema):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    specialite: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    numero_ordre: Optional[str] = None
    photo: Optional[str] = None
    est_actif: Optional[bool] = None
    service_id: Optional[int] = None
    service_ids: Optional[List[int]] = None


class DocteurOutSchema(Schema):
    id: int
    nom: str
    prenom: str
    specialite: str
    email: str
    telephone: str
    adresse: str
    numero_ordre: str
    photo: str
    est_actif: bool
    service_id: Optional[int] = None
    service_nom: Optional[str] = None
    service_ids: List[int] = []
    service_noms: List[str] = []
    date_enregistrement: str


def _docteur_out(d: Docteur) -> dict:
    svc_ids = list(d.services.values_list('id', flat=True))
    if d.service_id and d.service_id not in svc_ids:
        svc_ids.insert(0, d.service_id)
    svc_noms = list(d.services.values_list('nom', flat=True))
    if d.service and d.service.nom not in svc_noms:
        svc_noms.insert(0, d.service.nom)
    return {
        'id': d.id,
        'nom': d.nom,
        'prenom': d.prenom,
        'specialite': d.specialite,
        'email': d.email,
        'telephone': d.telephone,
        'adresse': d.adresse,
        'numero_ordre': d.numero_ordre,
        'photo': d.photo,
        'est_actif': d.est_actif,
        'service_id': d.service_id,
        'service_nom': d.service.nom if d.service else None,
        'service_ids': svc_ids,
        'service_noms': svc_noms,
        'user_id': d.user_id,
        'date_enregistrement': iso(d.date_enregistrement),
    }


def _sync_docteur_services(docteur: Docteur, service_ids: Optional[List[int]] = None) -> None:
    if service_ids is None:
        return
    docteur.services.set(service_ids)
    if service_ids and not docteur.service_id:
        docteur.service_id = service_ids[0]
        docteur.save(update_fields=['service_id'])


def _ensure_user(docteur: Docteur, password: str = 'medecin123') -> User:
    base = docteur.email.split('@')[0].replace('.', '_')
    username = base
    n = 1
    while User.objects.filter(username=username).exclude(email=docteur.email).exists():
        username = f"{base}{n}"
        n += 1

    user, created = User.objects.get_or_create(
        email=docteur.email,
        defaults={
            'username': username,
            'first_name': docteur.prenom,
            'last_name': docteur.nom,
            'role': 'MEDECIN',
            'telephone': docteur.telephone,
            'service_id': docteur.service_id,
        },
    )
    if not created:
        user.role = 'MEDECIN'
        user.first_name = docteur.prenom
        user.last_name = docteur.nom
        user.telephone = docteur.telephone
        user.service_id = docteur.service_id
    if created:
        user.set_password(password)
    user.save()
    docteur.user = user
    docteur.save(update_fields=['user'])
    return user


@personnel_router.get("/medecins", response=List[DocteurOutSchema], tags=["Personnel — Médecins"])
def lister_medecins(request, service_id: int = None):
    qs = Docteur.objects.select_related('service').prefetch_related('services')
    if service_id:
        qs = qs.filter(Q(service_id=service_id) | Q(services__id=service_id)).distinct()
    return [_docteur_out(d) for d in qs]


@personnel_router.post("/medecins", response=DocteurOutSchema, tags=["Personnel — Médecins"])
def creer_medecin(request, data: DocteurCreateSchema):
    payload = data.dict()
    service_ids = payload.pop('service_ids', None)
    service_id = payload.pop('service_id', None)
    docteur = Docteur(**payload)
    if service_id:
        docteur.service_id = service_id
    docteur.save()
    _sync_docteur_services(docteur, service_ids or ([service_id] if service_id else None))
    _ensure_user(docteur)
    return _docteur_out(docteur)


@personnel_router.get("/medecins/{medecin_id}", response=DocteurOutSchema, tags=["Personnel — Médecins"])
def detail_medecin(request, medecin_id: int):
    docteur = get_object_or_404(Docteur.objects.select_related('service'), id=medecin_id)
    return _docteur_out(docteur)


@personnel_router.put("/medecins/{medecin_id}", response=DocteurOutSchema, tags=["Personnel — Médecins"])
def modifier_medecin(request, medecin_id: int, data: DocteurUpdateSchema):
    docteur = get_object_or_404(Docteur, id=medecin_id)
    payload = {k: v for k, v in data.dict().items() if v is not None}
    service_ids = payload.pop('service_ids', None)
    service_id = payload.pop('service_id', None)
    for key, val in payload.items():
        setattr(docteur, key, val)
    if service_id is not None:
        docteur.service_id = service_id
    docteur.save()
    _sync_docteur_services(docteur, service_ids)
    if docteur.user:
        docteur.user.first_name = docteur.prenom
        docteur.user.last_name = docteur.nom
        docteur.user.email = docteur.email
        docteur.user.telephone = docteur.telephone
        docteur.user.service_id = docteur.service_id
        docteur.user.save()
    return _docteur_out(docteur)


@personnel_router.patch("/medecins/{medecin_id}/toggle", response=DocteurOutSchema, tags=["Personnel — Médecins"])
def toggle_medecin(request, medecin_id: int):
    docteur = get_object_or_404(Docteur.objects.select_related('service'), id=medecin_id)
    docteur.est_actif = not docteur.est_actif
    docteur.save(update_fields=['est_actif'])
    if docteur.user:
        docteur.user.is_active = docteur.est_actif
        docteur.user.save(update_fields=['is_active'])
    return _docteur_out(docteur)


@personnel_router.delete("/medecins/{medecin_id}", tags=["Personnel — Médecins"])
def supprimer_medecin(request, medecin_id: int):
    docteur = get_object_or_404(Docteur, id=medecin_id)
    user = docteur.user
    docteur.delete()
    if user:
        user.delete()
    return {"success": True}


# --- SECRÉTAIRES ---

class SecretaireOutSchema(Schema):
    id: int
    username: str
    nom_complet: str
    email: str
    telephone: str
    en_pause: bool
    service_id: Optional[int] = None
    service_nom: Optional[str] = None


@personnel_router.get("/secretaires", response=List[SecretaireOutSchema], tags=["Personnel — Secrétaires"])
def lister_secretaires(request):
    qs = User.objects.filter(role__in=['SECRETAIRE', 'SECRETAIRE_GENERALE']).select_related('service')
    return [
        {
            'id': u.id,
            'username': u.username,
            'nom_complet': u.get_full_name() or u.username,
            'email': u.email,
            'telephone': u.telephone or '',
            'en_pause': u.en_pause,
            'service_id': u.service_id,
            'service_nom': u.service.nom if u.service else None,
        }
        for u in qs
    ]


@personnel_router.patch("/secretaires/{user_id}/pause", response=SecretaireOutSchema, tags=["Personnel — Secrétaires"])
def toggle_pause_secretaire(request, user_id: int):
    u = get_object_or_404(User.objects.select_related('service'), id=user_id, role='SECRETAIRE')
    u.en_pause = not u.en_pause
    u.save(update_fields=['en_pause'])
    return {
        'id': u.id,
        'username': u.username,
        'nom_complet': u.get_full_name() or u.username,
        'email': u.email,
        'telephone': u.telephone or '',
        'en_pause': u.en_pause,
        'service_id': u.service_id,
        'service_nom': u.service.nom if u.service else None,
    }


# --- INFIRMIERS ---

class InfirmierCreateSchema(Schema):
    nom: str
    prenom: str
    email: str
    telephone: str
    numero_ordre: str = ''
    service_id: Optional[int] = None


class InfirmierUpdateSchema(Schema):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    numero_ordre: Optional[str] = None
    service_id: Optional[int] = None
    est_actif: Optional[bool] = None
    en_pause: Optional[bool] = None


class InfirmierOutSchema(Schema):
    id: int
    nom: str
    prenom: str
    email: str
    telephone: str
    numero_ordre: str
    est_actif: bool
    en_pause: bool
    service_id: Optional[int] = None
    service_nom: Optional[str] = None
    date_enregistrement: str


def _infirmier_out(i: Infirmier) -> dict:
    return {
        'id': i.id,
        'nom': i.nom,
        'prenom': i.prenom,
        'email': i.email,
        'telephone': i.telephone,
        'numero_ordre': i.numero_ordre,
        'est_actif': i.est_actif,
        'en_pause': i.en_pause,
        'service_id': i.service_id,
        'service_nom': i.service.nom if i.service else None,
        'date_enregistrement': iso(i.date_enregistrement),
    }


def _ensure_infirmier_user(infirmier: Infirmier, password: str = 'infirmier123') -> User:
    base = infirmier.email.split('@')[0].replace('.', '_')
    username = base
    n = 1
    while User.objects.filter(username=username).exclude(email=infirmier.email).exists():
        username = f"{base}{n}"
        n += 1
    user, created = User.objects.get_or_create(
        email=infirmier.email,
        defaults={
            'username': username,
            'first_name': infirmier.prenom,
            'last_name': infirmier.nom,
            'role': 'INFIRMIER',
            'telephone': infirmier.telephone,
            'service_id': infirmier.service_id,
        },
    )
    if not created:
        user.role = 'INFIRMIER'
        user.first_name = infirmier.prenom
        user.last_name = infirmier.nom
        user.telephone = infirmier.telephone
        user.service_id = infirmier.service_id
        user.en_pause = infirmier.en_pause
    if created:
        user.set_password(password)
    user.save()
    infirmier.user = user
    infirmier.save(update_fields=['user'])
    return user


@personnel_router.get("/infirmiers", response=List[InfirmierOutSchema], tags=["Personnel — Infirmiers"])
def lister_infirmiers(request, service_id: int = None):
    qs = Infirmier.objects.select_related('service').all()
    if service_id:
        qs = qs.filter(service_id=service_id)
    return [_infirmier_out(i) for i in qs]


@personnel_router.post("/infirmiers", response=InfirmierOutSchema, tags=["Personnel — Infirmiers"])
def creer_infirmier(request, data: InfirmierCreateSchema):
    payload = data.dict()
    service_id = payload.pop('service_id', None)
    infirmier = Infirmier(**payload)
    if service_id:
        infirmier.service_id = service_id
    infirmier.save()
    _ensure_infirmier_user(infirmier)
    return _infirmier_out(infirmier)


@personnel_router.patch("/infirmiers/{infirmier_id}/pause", response=InfirmierOutSchema, tags=["Personnel — Infirmiers"])
def toggle_pause_infirmier(request, infirmier_id: int):
    infirmier = get_object_or_404(Infirmier.objects.select_related('service'), id=infirmier_id)
    infirmier.en_pause = not infirmier.en_pause
    infirmier.save(update_fields=['en_pause'])
    if infirmier.user:
        infirmier.user.en_pause = infirmier.en_pause
        infirmier.user.save(update_fields=['en_pause'])
    return _infirmier_out(infirmier)


@personnel_router.patch("/infirmiers/{infirmier_id}/toggle", response=InfirmierOutSchema, tags=["Personnel — Infirmiers"])
def toggle_infirmier(request, infirmier_id: int):
    infirmier = get_object_or_404(Infirmier.objects.select_related('service'), id=infirmier_id)
    infirmier.est_actif = not infirmier.est_actif
    infirmier.save(update_fields=['est_actif'])
    if infirmier.user:
        infirmier.user.is_active = infirmier.est_actif
        infirmier.user.save(update_fields=['is_active'])
    return _infirmier_out(infirmier)


@personnel_router.delete("/infirmiers/{infirmier_id}", tags=["Personnel — Infirmiers"])
def supprimer_infirmier(request, infirmier_id: int):
    infirmier = get_object_or_404(Infirmier, id=infirmier_id)
    user = infirmier.user
    infirmier.delete()
    if user:
        user.delete()
    return {"success": True}
