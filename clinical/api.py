from ninja import Router, Schema
from ninja.errors import HttpError
from typing import List, Optional
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import get_object_or_404
from config.auth_helpers import require_admin, require_redirect_manager
from .models import Chambre, Lit, Admission, Service, LocalisationPatient, BanqueSang, SalleAttente, CasUrgence
from admission.models import Patient

clinical_router = Router()


# --- SCHÉMAS ---

class ServiceOutSchema(Schema):
    id: int
    code: str
    nom: str
    batiment: str
    etage: str
    telephone: str
    en_pause: bool = False
    secretaire_id: Optional[int] = None
    secretaire_nom: Optional[str] = None
    secretaire_en_pause: Optional[bool] = None
    infirmiers_total: int = 0
    infirmiers_en_service: int = 0


class ServiceCreateSchema(Schema):
    code: str
    nom: str
    batiment: str = 'Bâtiment A'
    etage: str = 'RDC'
    telephone: str = ''
    secretaire_id: Optional[int] = None


class ServiceUpdateSchema(Schema):
    nom: Optional[str] = None
    batiment: Optional[str] = None
    etage: Optional[str] = None
    telephone: Optional[str] = None
    secretaire_id: Optional[int] = None
    en_pause: Optional[bool] = None


class ChambreCreateSchema(Schema):
    numero: str
    type_chambre: str
    prix_journalier: float
    batiment: str = 'Bâtiment A'
    etage: str = '1'
    service_id: Optional[int] = None


class ChambreOutSchema(Schema):
    id: int
    numero: str
    type_chambre: str
    statut: str
    statut_label: str
    prix_journalier: Decimal
    batiment: str
    etage: str
    lits_total: int
    lits_occupes: int


class ChambreStatutSchema(Schema):
    statut: str


def _chambre_out(chambre: Chambre) -> dict:
    lits = list(chambre.lits.all())
    return {
        'id': chambre.id,
        'numero': chambre.numero,
        'type_chambre': chambre.type_chambre,
        'statut': chambre.statut,
        'statut_label': chambre.get_statut_display(),
        'prix_journalier': chambre.prix_journalier,
        'batiment': chambre.batiment,
        'etage': chambre.etage,
        'lits_total': len(lits),
        'lits_occupes': sum(1 for l in lits if l.est_occupe),
    }


class LitOutSchema(Schema):
    id: int
    chambre_id: int
    code_lit: str
    est_occupe: bool


class LitCreateSchema(Schema):
    chambre_id: int
    code_lit: str


class AdmissionCreateSchema(Schema):
    patient_id: int
    lit_id: int
    motif_hospitalisation: str


class AdmissionOutSchema(Schema):
    id: int
    patient_id: int
    patient_nom: str = ''
    lit_id: Optional[int] = None
    date_entree: str
    date_sortie: Optional[str] = None
    motif_hospitalisation: str
    frais_hebergement_total: Decimal
    est_cloture: bool


class LocalisationOutSchema(Schema):
    id: int
    patient_id: int
    patient_nom: str
    patient_sgl_id: str
    service_id: Optional[int] = None
    service_nom: Optional[str] = None
    batiment: str
    etage: str
    salle: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    statut: str
    statut_label: str
    date_mise_a_jour: str


class LocalisationCreateSchema(Schema):
    patient_id: int
    service_id: Optional[int] = None
    batiment: str = 'Bâtiment A'
    etage: str = 'RDC'
    salle: str = 'Accueil'
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    statut: str = 'ENREGISTRE'


class BanqueSangOutSchema(Schema):
    id: int
    groupe_sanguin: str
    numero_poche: str
    volume_ml: int
    date_collecte: str
    date_expiration: str
    statut: str


class BanqueSangCreateSchema(Schema):
    groupe_sanguin: str
    numero_poche: str
    volume_ml: int = 450
    date_collecte: str
    date_expiration: str
    donneur_id: str = ''


class StockSanguinSchema(Schema):
    groupe_sanguin: str
    total_ml: int
    poches_disponibles: int
    statut: str


def _localisation_out(loc: LocalisationPatient) -> dict:
    return {
        'id': loc.id,
        'patient_id': loc.patient_id,
        'patient_nom': f"{loc.patient.nom} {loc.patient.prenom}",
        'patient_sgl_id': loc.patient.sgl_id,
        'service_id': loc.service_id,
        'service_nom': loc.service.nom if loc.service else None,
        'batiment': loc.batiment,
        'etage': loc.etage,
        'salle': loc.salle,
        'latitude': float(loc.latitude) if loc.latitude else None,
        'longitude': float(loc.longitude) if loc.longitude else None,
        'statut': loc.statut,
        'statut_label': loc.get_statut_display(),
        'date_mise_a_jour': loc.date_mise_a_jour.isoformat(),
    }


# --- SERVICES & SECRÉTARIAT ---

def _service_out(s: Service) -> dict:
    from users.models import Infirmier
    infirmiers = Infirmier.objects.filter(service=s, est_actif=True)
    return {
        'id': s.id,
        'code': s.code,
        'nom': s.nom,
        'batiment': s.batiment,
        'etage': s.etage,
        'telephone': s.telephone,
        'en_pause': s.en_pause,
        'secretaire_id': s.secretaire_id,
        'secretaire_nom': s.secretaire.get_full_name() or s.secretaire.username if s.secretaire else None,
        'secretaire_en_pause': s.secretaire.en_pause if s.secretaire else None,
        'infirmiers_total': infirmiers.count(),
        'infirmiers_en_service': infirmiers.filter(en_pause=False).count(),
    }


@clinical_router.get("/services", response=List[ServiceOutSchema], tags=["Services & Secrétariat"])
def lister_services(request):
    return [_service_out(s) for s in Service.objects.select_related('secretaire').all()]


@clinical_router.post("/services", response=ServiceOutSchema, tags=["Services & Secrétariat"])
def creer_service(request, data: ServiceCreateSchema):
    require_admin(request)
    payload = data.dict()
    secretaire_id = payload.pop('secretaire_id', None)
    service = Service.objects.create(**payload)
    if secretaire_id:
        service.secretaire_id = secretaire_id
        service.save(update_fields=['secretaire_id'])
    return _service_out(service)


@clinical_router.patch("/services/{service_id}", response=ServiceOutSchema, tags=["Services & Secrétariat"])
def modifier_service(request, service_id: int, data: ServiceUpdateSchema):
    require_admin(request)
    service = get_object_or_404(Service.objects.select_related('secretaire'), id=service_id)
    for k, v in {k: v for k, v in data.dict().items() if v is not None}.items():
        setattr(service, k, v)
    service.save()
    service.refresh_from_db()
    return _service_out(service)


@clinical_router.patch("/services/{service_id}/pause", response=ServiceOutSchema, tags=["Services & Secrétariat"])
def toggle_pause_service(request, service_id: int):
    require_redirect_manager(request)
    service = get_object_or_404(Service.objects.select_related('secretaire'), id=service_id)
    service.en_pause = not service.en_pause
    service.save(update_fields=['en_pause'])
    return _service_out(service)


# --- CHAMBRES & LITS ---

@clinical_router.get("/chambres", response=List[ChambreOutSchema], tags=["Gestion des Hospitalisations"])
def lister_chambres(request):
    return [_chambre_out(c) for c in Chambre.objects.prefetch_related('lits').all()]


@clinical_router.patch("/chambres/{chambre_id}/statut", response=ChambreOutSchema, tags=["Gestion des Hospitalisations"])
def changer_statut_chambre(request, chambre_id: int, data: ChambreStatutSchema):
    chambre = get_object_or_404(Chambre, id=chambre_id)
    statuts_valides = {s[0] for s in Chambre.STATUT_CHOICES}
    if data.statut not in statuts_valides:
        raise HttpError(400, f"Statut invalide. Valeurs acceptées : {', '.join(statuts_valides)}")
    chambre.statut = data.statut
    chambre.save(update_fields=['statut'])
    return _chambre_out(chambre)


@clinical_router.post("/chambres", response=ChambreOutSchema, tags=["Gestion des Hospitalisations"])
def creer_chambre(request, data: ChambreCreateSchema):
    payload = data.dict()
    service_id = payload.pop('service_id', None)
    chambre = Chambre(**payload)
    if service_id:
        chambre.service_id = service_id
    chambre.save()
    return _chambre_out(chambre)


@clinical_router.get("/lits", response=List[LitOutSchema], tags=["Gestion des Hospitalisations"])
def lister_lits(request):
    return [
        {'id': l.id, 'chambre_id': l.chambre_id, 'code_lit': l.code_lit, 'est_occupe': l.est_occupe}
        for l in Lit.objects.all()
    ]


@clinical_router.post("/lits", response=LitOutSchema, tags=["Gestion des Hospitalisations"])
def creer_lit(request, data: LitCreateSchema):
    chambre = get_object_or_404(Chambre, id=data.chambre_id)
    lit = Lit.objects.create(chambre=chambre, code_lit=data.code_lit)
    return {'id': lit.id, 'chambre_id': chambre.id, 'code_lit': lit.code_lit, 'est_occupe': lit.est_occupe}


# --- ADMISSIONS ---

@clinical_router.get("/admissions", response=List[AdmissionOutSchema], tags=["Gestion des Hospitalisations"])
def lister_admissions(request):
    result = []
    for a in Admission.objects.select_related('patient').all().order_by('-date_entree'):
        result.append({
            'id': a.id,
            'patient_id': a.patient_id,
            'patient_nom': f"{a.patient.nom} {a.patient.prenom}",
            'lit_id': a.lit_id,
            'date_entree': a.date_entree.isoformat(),
            'date_sortie': a.date_sortie.isoformat() if a.date_sortie else None,
            'motif_hospitalisation': a.motif_hospitalisation,
            'frais_hebergement_total': a.frais_hebergement_total,
            'est_cloture': a.est_cloture,
        })
    return result


@clinical_router.post("/admissions", response=AdmissionOutSchema, tags=["Gestion des Hospitalisations"])
def hospitaliser_patient(request, data: AdmissionCreateSchema):
    patient = get_object_or_404(Patient, id=data.patient_id)
    lit = get_object_or_404(Lit, id=data.lit_id)
    if lit.est_occupe:
        raise HttpError(400, "Ce lit est déjà occupé par un autre patient.")
    lit.est_occupe = True
    lit.save()
    admission = Admission.objects.create(
        patient=patient,
        lit=lit,
        motif_hospitalisation=data.motif_hospitalisation,
    )
    lit.chambre.sync_statut_depuis_lits()
    LocalisationPatient.objects.create(
        patient=patient,
        service=lit.chambre.service,
        batiment=lit.chambre.batiment,
        etage=lit.chambre.etage,
        salle=f"Chambre {lit.chambre.numero} — Lit {lit.code_lit}",
        statut='HOSPITALISE',
    )
    return {
        'id': admission.id,
        'patient_id': admission.patient_id,
        'patient_nom': f"{patient.nom} {patient.prenom}",
        'lit_id': admission.lit_id,
        'date_entree': admission.date_entree.isoformat(),
        'date_sortie': None,
        'motif_hospitalisation': admission.motif_hospitalisation,
        'frais_hebergement_total': admission.frais_hebergement_total,
        'est_cloture': admission.est_cloture,
    }


@clinical_router.get("/admissions/patient/{patient_id}", response=List[AdmissionOutSchema], tags=["Gestion des Hospitalisations"])
def admissions_patient(request, patient_id: int):
    result = []
    for a in Admission.objects.filter(patient_id=patient_id).select_related('patient').order_by('-date_entree'):
        result.append({
            'id': a.id,
            'patient_id': a.patient_id,
            'patient_nom': f"{a.patient.nom} {a.patient.prenom}",
            'lit_id': a.lit_id,
            'date_entree': a.date_entree.isoformat(),
            'date_sortie': a.date_sortie.isoformat() if a.date_sortie else None,
            'motif_hospitalisation': a.motif_hospitalisation,
            'frais_hebergement_total': a.frais_hebergement_total,
            'est_cloture': a.est_cloture,
        })
    return result


@clinical_router.post("/admissions/{admission_id}/sortie", response=AdmissionOutSchema, tags=["Gestion des Hospitalisations"])
def sortie_patient(request, admission_id: int):
    admission = get_object_or_404(Admission, id=admission_id)
    if admission.est_cloture:
        return {
            'id': admission.id,
            'patient_id': admission.patient_id,
            'patient_nom': f"{admission.patient.nom} {admission.patient.prenom}",
            'lit_id': admission.lit_id,
            'date_entree': admission.date_entree.isoformat(),
            'date_sortie': admission.date_sortie.isoformat() if admission.date_sortie else None,
            'motif_hospitalisation': admission.motif_hospitalisation,
            'frais_hebergement_total': admission.frais_hebergement_total,
            'est_cloture': admission.est_cloture,
        }
    admission.date_sortie = timezone.now()
    duree = (admission.date_sortie - admission.date_entree).days
    if duree <= 0:
        duree = 1
    if admission.lit and admission.lit.chambre:
        admission.frais_hebergement_total = Decimal(duree) * admission.lit.chambre.prix_journalier
        chambre = admission.lit.chambre
        admission.lit.est_occupe = False
        admission.lit.save()
        chambre.sync_statut_depuis_lits()
    admission.est_cloture = True
    admission.save()
    LocalisationPatient.objects.create(
        patient=admission.patient,
        batiment='Sortie',
        etage='—',
        salle='Accueil sortie',
        statut='SORTI',
    )
    return {
        'id': admission.id,
        'patient_id': admission.patient_id,
        'patient_nom': f"{admission.patient.nom} {admission.patient.prenom}",
        'lit_id': admission.lit_id,
        'date_entree': admission.date_entree.isoformat(),
        'date_sortie': admission.date_sortie.isoformat(),
        'motif_hospitalisation': admission.motif_hospitalisation,
        'frais_hebergement_total': admission.frais_hebergement_total,
        'est_cloture': admission.est_cloture,
    }
# --- GÉOLOCALISATION PATIENT ---

@clinical_router.get("/localisations", response=List[LocalisationOutSchema], tags=["Géolocalisation Patient"])
def lister_localisations(request):
    locs = LocalisationPatient.objects.select_related('patient', 'service').all()[:100]
    seen = set()
    result = []
    for loc in locs:
        if loc.patient_id in seen:
            continue
        seen.add(loc.patient_id)
        result.append(_localisation_out(loc))
    return result


@clinical_router.get("/localisations/patient/{patient_id}", response=List[LocalisationOutSchema], tags=["Géolocalisation Patient"])
def historique_localisation(request, patient_id: int):
    locs = LocalisationPatient.objects.filter(patient_id=patient_id).select_related('patient', 'service')
    return [_localisation_out(loc) for loc in locs]


@clinical_router.post("/localisations", response=LocalisationOutSchema, tags=["Géolocalisation Patient"])
def mettre_a_jour_localisation(request, data: LocalisationCreateSchema):
    from config.geo import BUILDING_COORDS, HOSPITAL_CENTER
    patient = get_object_or_404(Patient, id=data.patient_id)
    lat = data.latitude
    lng = data.longitude
    if lat is None or lng is None:
        lat, lng = BUILDING_COORDS.get(data.batiment, HOSPITAL_CENTER)
    loc = LocalisationPatient.objects.create(
        patient=patient,
        service_id=data.service_id,
        batiment=data.batiment,
        etage=data.etage,
        salle=data.salle,
        latitude=lat,
        longitude=lng,
        statut=data.statut,
    )
    return _localisation_out(loc)


# --- BANQUE DE SANG ---

@clinical_router.get("/banque-sang", response=List[BanqueSangOutSchema], tags=["Banque de Sang"])
def lister_banque_sang(request):
    return [
        {
            'id': b.id,
            'groupe_sanguin': b.groupe_sanguin,
            'numero_poche': b.numero_poche,
            'volume_ml': b.volume_ml,
            'date_collecte': b.date_collecte.isoformat(),
            'date_expiration': b.date_expiration.isoformat(),
            'statut': b.statut,
        }
        for b in BanqueSang.objects.all().order_by('groupe_sanguin')
    ]


@clinical_router.get("/banque-sang/stock", response=List[StockSanguinSchema], tags=["Banque de Sang"])
def stock_sanguin(request):
    groupes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    result = []
    for g in groupes:
        poches = BanqueSang.objects.filter(groupe_sanguin=g, statut='DISPONIBLE')
        total = sum(p.volume_ml for p in poches)
        count = poches.count()
        if total < 500:
            statut = 'CRITIQUE'
        elif total < 1500:
            statut = 'BAS'
        else:
            statut = 'NORMAL'
        result.append({
            'groupe_sanguin': g,
            'total_ml': total,
            'poches_disponibles': count,
            'statut': statut,
        })
    return result


@clinical_router.post("/banque-sang", response=BanqueSangOutSchema, tags=["Banque de Sang"])
def ajouter_poche(request, data: BanqueSangCreateSchema):
    from datetime import date
    poche = BanqueSang.objects.create(**data.dict())
    return {
        'id': poche.id,
        'groupe_sanguin': poche.groupe_sanguin,
        'numero_poche': poche.numero_poche,
        'volume_ml': poche.volume_ml,
        'date_collecte': poche.date_collecte.isoformat(),
        'date_expiration': poche.date_expiration.isoformat(),
        'statut': poche.statut,
    }


# --- SALLE D'ATTENTE ---

class SalleAttenteCreateSchema(Schema):
    patient_id: int
    motif: str = ''
    priorite: str = 'NORMAL'
    type_file: str = 'STANDARD'


class SalleAttenteOutSchema(Schema):
    id: int
    patient_id: int
    patient_nom: str
    numero_identite: str
    genre_label: str
    telephone: str
    age: int
    situation_familiale: str
    motif: str
    priorite: str
    type_file: str
    type_file_label: str
    est_privilegie: bool = False
    carte_type: Optional[str] = None
    carte_numero: Optional[str] = None
    taux_reduction: Optional[int] = None
    statut: str
    statut_label: str
    date_arrivee: str


def _patient_privilege_info(patient):
    from admission.models import ClientPrivilegie
    from django.utils import timezone
    carte = ClientPrivilegie.objects.filter(patient=patient, est_actif=True).first()
    if not carte:
        return None
    if carte.date_expiration and carte.date_expiration < timezone.now().date():
        return None
    return carte


def _resolve_type_file(patient, requested: str = 'STANDARD') -> str:
    valid = {c[0] for c in SalleAttente.TYPE_FILE_CHOICES}
    if requested in valid:
        tf = requested
    else:
        tf = 'STANDARD'
    if tf == 'STANDARD' and _patient_privilege_info(patient):
        return 'PRIVILEGE'
    return tf


def _attente_out(a: SalleAttente) -> dict:
    p = a.patient
    carte = _patient_privilege_info(p)
    return {
        'id': a.id, 'patient_id': p.id,
        'patient_nom': f"{p.nom} {p.prenom}",
        'numero_identite': p.numero_identite or p.sgl_id,
        'genre_label': p.get_genre_display(),
        'telephone': p.telephone, 'age': p.age,
        'situation_familiale': p.situation_familiale or '—',
        'motif': a.motif, 'priorite': a.priorite,
        'type_file': a.type_file,
        'type_file_label': a.get_type_file_display(),
        'est_privilegie': carte is not None,
        'carte_type': carte.get_type_carte_display() if carte else None,
        'carte_numero': carte.numero_carte if carte else None,
        'taux_reduction': carte.taux_reduction if carte else None,
        'statut': a.statut, 'statut_label': a.get_statut_display(),
        'date_arrivee': a.date_arrivee.isoformat(),
    }


@clinical_router.get("/salle-attente", response=List[SalleAttenteOutSchema], tags=["Salle d'attente"])
def lister_salle_attente(request, type_file: str = ''):
    qs = SalleAttente.objects.filter(statut__in=['EN_ATTENTE', 'EN_CONSULTATION']).select_related('patient')
    if type_file in dict(SalleAttente.TYPE_FILE_CHOICES):
        qs = qs.filter(type_file=type_file)
    return [_attente_out(a) for a in qs]


@clinical_router.post("/salle-attente", response=SalleAttenteOutSchema, tags=["Salle d'attente"])
def ajouter_salle_attente(request, data: SalleAttenteCreateSchema):
    patient = get_object_or_404(Patient, id=data.patient_id)
    type_file = _resolve_type_file(patient, data.type_file)
    entry = SalleAttente.objects.create(
        patient=patient,
        motif=data.motif,
        priorite=data.priorite,
        type_file=type_file,
    )
    salle = "Salon VIP — Clients privilégiés" if type_file == 'PRIVILEGE' else "Salle d'attente"
    LocalisationPatient.objects.create(
        patient=patient, batiment='Bâtiment A', etage='RDC',
        salle=salle, statut='EN_ATTENTE',
    )
    return _attente_out(entry)


@clinical_router.patch("/salle-attente/{entry_id}/statut", response=SalleAttenteOutSchema, tags=["Salle d'attente"])
def changer_statut_attente(request, entry_id: int, data: ChambreStatutSchema):
    entry = get_object_or_404(SalleAttente.objects.select_related('patient'), id=entry_id)
    if data.statut in dict(SalleAttente.STATUT_CHOICES):
        entry.statut = data.statut
        entry.save(update_fields=['statut'])
    return _attente_out(entry)


@clinical_router.delete("/salle-attente/{entry_id}", tags=["Salle d'attente"])
def retirer_salle_attente(request, entry_id: int):
    get_object_or_404(SalleAttente, id=entry_id).delete()
    return {"success": True}


# --- URGENCES ---

class UrgenceCreateSchema(Schema):
    patient_id: int
    diagnostic: str
    situation: str = 'NORMAL'
    notes: str = ''


class UrgenceUpdateSchema(Schema):
    diagnostic: Optional[str] = None
    situation: Optional[str] = None
    notes: Optional[str] = None
    traitement: Optional[str] = None
    examen_biologique: Optional[str] = None
    examen_radiologique: Optional[str] = None
    statut: Optional[str] = None


class UrgenceOutSchema(Schema):
    id: int
    patient_id: int
    patient_nom: str
    diagnostic: str
    situation: str
    situation_label: str
    notes: str
    traitement: str
    examen_biologique: str
    examen_radiologique: str
    statut: str
    date_admission: str


def _urgence_out(u: CasUrgence) -> dict:
    return {
        'id': u.id, 'patient_id': u.patient_id,
        'patient_nom': f"{u.patient.nom} {u.patient.prenom}",
        'diagnostic': u.diagnostic, 'situation': u.situation,
        'situation_label': u.get_situation_display(),
        'notes': u.notes, 'traitement': u.traitement,
        'examen_biologique': u.examen_biologique,
        'examen_radiologique': u.examen_radiologique,
        'statut': u.statut, 'date_admission': u.date_admission.isoformat(),
    }


@clinical_router.get("/urgences", response=List[UrgenceOutSchema], tags=["Urgences"])
def lister_urgences(request):
    qs = CasUrgence.objects.select_related('patient').exclude(statut='SORTI')
    return [_urgence_out(u) for u in qs]


@clinical_router.post("/urgences", response=UrgenceOutSchema, tags=["Urgences"])
def creer_urgence(request, data: UrgenceCreateSchema):
    patient = get_object_or_404(Patient, id=data.patient_id)
    cas = CasUrgence.objects.create(
        patient=patient, diagnostic=data.diagnostic,
        situation=data.situation, notes=data.notes,
    )
    LocalisationPatient.objects.create(
        patient=patient, batiment='Bâtiment A', etage='RDC',
        salle='Urgences', statut='EN_CONSULTATION',
    )
    return _urgence_out(cas)


@clinical_router.put("/urgences/{cas_id}", response=UrgenceOutSchema, tags=["Urgences"])
def modifier_urgence(request, cas_id: int, data: UrgenceUpdateSchema):
    cas = get_object_or_404(CasUrgence.objects.select_related('patient'), id=cas_id)
    for k, v in {k: v for k, v in data.dict().items() if v is not None}.items():
        setattr(cas, k, v)
    cas.save()
    return _urgence_out(cas)


@clinical_router.delete("/urgences/{cas_id}", tags=["Urgences"])
def supprimer_urgence(request, cas_id: int):
    get_object_or_404(CasUrgence, id=cas_id).delete()
    return {"success": True}
