from ninja import Router, Schema
from typing import List, Optional
from datetime import date
from django.shortcuts import get_object_or_404
from django.utils import timezone
from config.serializers import iso
from .models import Patient, Assurance, Abonne, RendezVous, NotePatient, PatientChatMessage

from config.geo import HOSPITAL_CENTER, BUILDING_COORDS

admission_router = Router()


class AssuranceSchema(Schema):
    id: int
    nom: str
    code_assurance: str
    taux_couverture: int


class AssuranceCreateSchema(Schema):
    nom: str
    code_assurance: str
    taux_couverture: int
    adresse: str = None


class PatientCreateSchema(Schema):
    sgl_id: Optional[str] = None
    nom: str
    prenom: str
    date_naissance: date
    genre: str
    telephone: str
    email: Optional[str] = None
    adresse: str = None
    numero_identite: str = None
    situation_familiale: str = None
    nombre_enfants: int = 0
    profession: str = None
    poids_kg: float = None
    taille_m: float = None
    groupe_sanguin: str = None
    informations_medicales: str = None
    allergies: str = None
    antecedents_medicaux: str = None
    contact_urgence_nom: str = None
    contact_urgence_telephone: str = None
    contact_urgence_lien: str = None
    assurance_id: int = None
    numero_assure: str = None
    abonne_id: int = None


class PatientOutSchema(Schema):
    id: int
    sgl_id: str
    nom: str
    prenom: str
    date_naissance: date
    genre: str
    genre_label: str
    age: int
    telephone: str
    adresse: Optional[str] = None
    numero_identite: Optional[str] = None
    situation_familiale: Optional[str] = None
    nombre_enfants: int = 0
    profession: Optional[str] = None
    poids_kg: Optional[float] = None
    taille_m: Optional[float] = None
    groupe_sanguin: Optional[str] = None
    informations_medicales: Optional[str] = None
    allergies: Optional[str] = None
    antecedents_medicaux: Optional[str] = None
    contact_urgence_nom: Optional[str] = None
    contact_urgence_telephone: Optional[str] = None
    contact_urgence_lien: Optional[str] = None
    assurance_nom: Optional[str] = None
    qr_code: Optional[str] = None
    statut: Optional[str] = None
    statut_label: Optional[str] = None
    nb_produits: int = 0
    email: Optional[str] = None
    date_enregistrement: str


def _compute_patient_statut(patient: Patient) -> tuple:
    from clinical.models import SalleAttente, Admission, CasUrgence, LocalisationPatient

    urgence = CasUrgence.objects.filter(patient=patient).exclude(statut='SORTI').order_by('-date_admission').first()
    if urgence:
        return 'URGENCE', f"Urgence — {urgence.get_situation_display()}"

    admission = Admission.objects.filter(patient=patient, est_cloture=False).select_related('lit__chambre').first()
    if admission and admission.lit:
        return 'HOSPITALISE', f"Hospitalisé — Ch. {admission.lit.chambre.numero} Lit {admission.lit.code_lit}"

    attente = SalleAttente.objects.filter(
        patient=patient, statut__in=['EN_ATTENTE', 'EN_CONSULTATION'],
    ).order_by('-date_arrivee').first()
    if attente:
        return attente.statut, attente.get_statut_display()

    loc = LocalisationPatient.objects.filter(patient=patient).order_by('-date_mise_a_jour').first()
    if loc:
        return loc.statut, loc.get_statut_display()

    return 'EXTERNE', 'Hors établissement'


def _patient_produits_count(patient: Patient) -> int:
    from pharmacy.models import PrescriptionPharmacie
    return PrescriptionPharmacie.objects.filter(patient=patient).count()


def _next_sgl_id() -> str:
    year = timezone.now().year
    prefix = f'SGHL-{year}-'
    count = Patient.objects.filter(sgl_id__startswith=prefix).count() + 1
    return f'{prefix}{count:03d}'


def _resolve_patient_by_email(email: str) -> Optional[Patient]:
    if not email:
        return None
    patient = Patient.objects.filter(email__iexact=email).first()
    if patient:
        return patient
    from users.models import User
    user = User.objects.filter(email__iexact=email, role='PATIENT').first()
    if not user:
        return None
    patient = Patient.objects.filter(user=user).first()
    if not patient:
        patient = Patient.objects.filter(email__iexact=user.email).first()
        if patient and not patient.user_id:
            patient.user = user
            patient.save(update_fields=['user'])
    return patient


def _search_patients_by_name(nom: str):
    from django.db.models import Q
    q = nom.strip()
    if not q or len(q) < 2:
        return Patient.objects.none()
    tokens = [t for t in q.split() if t]
    qs = Patient.objects.all()
    for token in tokens:
        qs = qs.filter(Q(nom__icontains=token) | Q(prenom__icontains=token))
    return qs.order_by('nom', 'prenom')[:20]


def _name_matches_patient(nom: str, patient: Patient) -> bool:
    q = nom.strip().lower()
    if not q:
        return False
    full = f"{patient.nom} {patient.prenom}".lower()
    tokens = [t.lower() for t in q.split() if t]
    return all(t in full for t in tokens)


def _slug_email_part(text: str) -> str:
    import re
    import unicodedata
    raw = unicodedata.normalize('NFKD', (text or '')).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^a-z0-9]+', '.', raw.lower()).strip('.')
    return slug or 'patient'


def _default_patient_email(patient: Patient) -> str:
    base = f"{_slug_email_part(patient.prenom)}.{_slug_email_part(patient.nom)}"
    email = f"{base}@patient.sghl.com"
    n = 1
    while Patient.objects.filter(email__iexact=email).exclude(pk=patient.pk).exists():
        n += 1
        email = f"{base}{n}@patient.sghl.com"
    return email


def ensure_patient_portal(patient: Patient, email: Optional[str] = None) -> str:
    """Attribue un email et un compte PATIENT pour le portail."""
    addr = (email or patient.email or '').strip().lower()
    if not addr:
        addr = _default_patient_email(patient)
    _link_patient_portal(patient, addr)
    return addr


def _link_patient_portal(patient: Patient, email: str):
    from users.models import User
    email = email.strip().lower()
    patient.email = email
    patient.save(update_fields=['email'])
    username = email.split('@')[0].replace('.', '_').replace('-', '_')[:30]
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': username,
            'first_name': patient.prenom,
            'last_name': patient.nom,
            'role': 'PATIENT',
        },
    )
    if not created:
        user.role = 'PATIENT'
        user.save(update_fields=['role'])
    if not user.has_usable_password():
        user.set_password('patient123')
        user.save(update_fields=['password'])
    if not patient.user_id:
        patient.user = user
        patient.save(update_fields=['user'])


def _patient_out(patient: Patient) -> dict:
    statut, statut_label = _compute_patient_statut(patient)
    return {
        'id': patient.id,
        'sgl_id': patient.sgl_id,
        'nom': patient.nom,
        'prenom': patient.prenom,
        'date_naissance': patient.date_naissance,
        'genre': patient.genre,
        'genre_label': patient.get_genre_display(),
        'age': patient.age,
        'telephone': patient.telephone,
        'adresse': patient.adresse,
        'numero_identite': patient.numero_identite,
        'situation_familiale': patient.situation_familiale,
        'nombre_enfants': patient.nombre_enfants,
        'profession': patient.profession,
        'poids_kg': float(patient.poids_kg) if patient.poids_kg else None,
        'taille_m': float(patient.taille_m) if patient.taille_m else None,
        'groupe_sanguin': patient.groupe_sanguin,
        'informations_medicales': patient.informations_medicales,
        'allergies': patient.allergies,
        'antecedents_medicaux': patient.antecedents_medicaux,
        'contact_urgence_nom': patient.contact_urgence_nom,
        'contact_urgence_telephone': patient.contact_urgence_telephone,
        'contact_urgence_lien': patient.contact_urgence_lien,
        'assurance_nom': patient.assurance.nom if patient.assurance else None,
        'date_enregistrement': iso(patient.date_enregistrement),
        'qr_code': str(patient.qr_code),
        'statut': statut,
        'statut_label': statut_label,
        'nb_produits': _patient_produits_count(patient),
        'email': patient.email or None,
    }


@admission_router.get("/assurances", response=List[AssuranceSchema], tags=["Réception & Assurances"])
def lister_assurances(request):
    return list(Assurance.objects.all().order_by('nom'))


@admission_router.post("/assurances", response=AssuranceSchema, tags=["Réception & Assurances"])
def creer_assurance(request, data: AssuranceCreateSchema):
    assurance = Assurance.objects.create(**data.dict())
    return assurance


@admission_router.post("/patients", response=PatientOutSchema, tags=["Réception & Enregistrement Malades"])
def enregistrer_patient(request, data: PatientCreateSchema):
    payload = data.dict()
    assurance_id = payload.pop("assurance_id", None)
    abonne_id = payload.pop("abonne_id", None)
    portal_email = payload.pop("email", None)
    if not payload.get('sgl_id'):
        payload['sgl_id'] = _next_sgl_id()

    patient = Patient(**payload)
    if assurance_id:
        patient.assurance = Assurance.objects.get(id=assurance_id)
    if abonne_id:
        patient.abonne = Abonne.objects.get(id=abonne_id)

    patient.save()
    portal_email = ensure_patient_portal(patient, portal_email)
    patient.refresh_from_db()
    from clinical.models import LocalisationPatient
    from core.services import log_activity
    log_activity(request, 'Nouveau patient enregistré', 'Patients', f'{patient.sgl_id} — {patient.nom} {patient.prenom}')
    LocalisationPatient.objects.create(
        patient=patient,
        batiment='Bâtiment A',
        etage='RDC',
        salle='Accueil — Réception',
        statut='ENREGISTRE',
        latitude=HOSPITAL_CENTER[0],
        longitude=HOSPITAL_CENTER[1],
    )
    return _patient_out(patient)


@admission_router.get("/patients", response=List[PatientOutSchema], tags=["Réception & Enregistrement Malades"])
def lister_patients(request):
    return [_patient_out(p) for p in Patient.objects.all().order_by('-date_enregistrement')]


@admission_router.post("/patients/sync-portail", tags=["Réception & Enregistrement Malades"])
def synchroniser_portails_patients(request):
    """Crée email + compte PATIENT pour tous les dossiers admis."""
    synced = []
    for p in Patient.objects.all().order_by('id'):
        email = ensure_patient_portal(p, p.email)
        synced.append({'id': p.id, 'nom': f"{p.nom} {p.prenom}", 'email': email})
    return {'count': len(synced), 'patients': synced}


def _match_patients_by_local(local: str):
    """Associe emmanuel ou emmanuel.massassi à des dossiers patients."""
    local = (local or '').strip().lower()
    if not local:
        return []

    if '.' in local:
        prenom_slug, nom_slug = local.split('.', 1)[0], local.rsplit('.', 1)[-1]
        matched = []
        for p in Patient.objects.all().only('id', 'nom', 'prenom', 'email', 'user_id'):
            if _slug_email_part(p.prenom) == prenom_slug and _slug_email_part(p.nom) == nom_slug:
                matched.append(p)
        return matched

    return list(
        Patient.objects.filter(prenom__icontains=local)
        .order_by('nom', 'prenom')[:15]
    )


def resolve_patient_lookup(raw: str):
    """
    Recherche un patient par email portail, alias @sghl.com ou nom/prénom.
    Retourne (patient, message_erreur).
    """
    import re
    from django.db.models import Q

    raw = (raw or '').strip()
    if not raw:
        return None, 'Entrez un email portail ou le nom du patient.'

    email_match = re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', raw, re.I)
    if email_match:
        email = email_match.group(0).lower()
        patient = _resolve_patient_by_email(email)
        if patient:
            ensure_patient_portal(patient, patient.email)
            return patient, None

        local, _, domain = email.partition('@')
        domain = domain.lower()
        if domain == 'sghl.com':
            portal_email = f'{local}@patient.sghl.com'
            patient = _resolve_patient_by_email(portal_email)
            if patient:
                return patient, None

            matched = _match_patients_by_local(local)
            if len(matched) == 1:
                ensure_patient_portal(matched[0])
                return matched[0], None
            if len(matched) > 1:
                hints = [f'{p.nom} {p.prenom} → {ensure_patient_portal(p)}' for p in matched]
                return None, 'Plusieurs patients trouvés :\n' + '\n'.join(hints)

    tokens = [t for t in re.sub(r'@', ' ', raw).split() if len(t) >= 2]
    if tokens:
        qs = Patient.objects.all()
        for token in tokens:
            qs = qs.filter(Q(nom__icontains=token) | Q(prenom__icontains=token))
        results = list(qs.order_by('nom', 'prenom')[:15])
        if len(results) == 1:
            ensure_patient_portal(results[0])
            return results[0], None
        if len(results) > 1:
            hints = [f'{p.nom} {p.prenom} → {p.email or ensure_patient_portal(p)}' for p in results]
            return None, 'Plusieurs patients — précisez le nom ou utilisez l\'email portail :\n' + '\n'.join(hints)

    return None, (
        'Aucun patient trouvé.\n'
        'Exemples : Mukendi Joseph · patient@sghl.com · emmanuel.massassi@patient.sghl.com'
    )


@admission_router.get("/patient-email", response=PatientOutSchema, tags=["Réception & Enregistrement Malades"])
def patient_par_email(request, email: str):
    from ninja.errors import HttpError
    patient, err = resolve_patient_lookup(email)
    if not patient:
        raise HttpError(404, err or "Aucun patient trouvé")
    return _patient_out(patient)


@admission_router.get("/patients/{patient_id}", response=PatientOutSchema, tags=["Réception & Enregistrement Malades"])
def detail_patient(request, patient_id: int):
    patient = get_object_or_404(Patient, id=patient_id)
    return _patient_out(patient)


class PatientUpdateSchema(Schema):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    profession: Optional[str] = None
    poids_kg: Optional[float] = None
    taille_m: Optional[float] = None
    groupe_sanguin: Optional[str] = None
    informations_medicales: Optional[str] = None
    allergies: Optional[str] = None
    antecedents_medicaux: Optional[str] = None
    contact_urgence_nom: Optional[str] = None
    contact_urgence_telephone: Optional[str] = None
    contact_urgence_lien: Optional[str] = None
    assurance_id: Optional[int] = None
    numero_assure: Optional[str] = None


@admission_router.patch("/patients/{patient_id}", response=PatientOutSchema, tags=["Réception & Enregistrement Malades"])
def modifier_patient(request, patient_id: int, data: PatientUpdateSchema):
    patient = get_object_or_404(Patient, id=patient_id)
    payload = data.dict(exclude_unset=True)
    assurance_id = payload.pop('assurance_id', None)
    for field, value in payload.items():
        setattr(patient, field, value)
    if assurance_id is not None:
        patient.assurance = Assurance.objects.get(id=assurance_id) if assurance_id else None
    patient.save()
    from core.services import log_activity
    log_activity(request, 'Modification dossier patient', 'Patients', f'{patient.sgl_id} — {patient.nom} {patient.prenom}')
    return _patient_out(patient)


@admission_router.get("/patients/{patient_id}/produits", tags=["Réception & Enregistrement Malades"])
def produits_patient(request, patient_id: int):
    from pharmacy.models import PrescriptionPharmacie
    patient = get_object_or_404(Patient, id=patient_id)
    return [
        {
            'id': p.id,
            'medicament': p.medicament.nom,
            'quantite': p.quantite_delivree,
            'prix_unitaire': float(p.medicament.prix_unitaire),
            'montant': float(p.frais_pharmacie_total),
            'est_paye': p.est_paye,
            'date_dispensation': iso(p.date_dispensation),
        }
        for p in PrescriptionPharmacie.objects.filter(patient=patient).select_related('medicament').order_by('-date_dispensation')
    ]


@admission_router.get("/mon-profil", response=PatientOutSchema, tags=["Espace Patient"])
def mon_profil_patient(request, email: str):
    patient = _resolve_patient_by_email(email)
    if not patient:
        from ninja.errors import HttpError
        raise HttpError(404, "Aucun dossier patient associé à cet email")
    return _patient_out(patient)


@admission_router.get("/mon-dossier", tags=["Espace Patient"])
def mon_dossier_patient(request, email: str):
    patient = _resolve_patient_by_email(email)
    if not patient:
        from ninja.errors import HttpError
        raise HttpError(404, "Aucun dossier patient associé à cet email")
    return _build_dossier_patient(patient)


class PatientSearchSchema(Schema):
    id: int
    nom: str
    prenom: str
    sgl_id: str
    numero_identite: Optional[str] = None
    age: int
    telephone: str


@admission_router.get("/acces-patient/recherche", response=List[PatientSearchSchema], tags=["Espace Patient"])
def rechercher_patient_par_nom(request, nom: str):
    return [
        {
            'id': p.id,
            'nom': p.nom,
            'prenom': p.prenom,
            'sgl_id': p.sgl_id,
            'numero_identite': p.numero_identite,
            'age': p.age,
            'telephone': p.telephone,
        }
        for p in _search_patients_by_name(nom)
    ]


@admission_router.get("/acces-patient/dossier", tags=["Espace Patient"])
def dossier_patient_par_nom(request, nom: str, patient_id: int):
    from ninja.errors import HttpError
    patient = get_object_or_404(Patient, id=patient_id)
    if not _name_matches_patient(nom, patient):
        raise HttpError(403, "Le nom saisi ne correspond pas à ce dossier")
    return _build_dossier_patient(patient)


def _build_dossier_patient(patient: Patient) -> dict:
    from consultation.models import Consultation, Ordonnance
    from clinical.models import Admission, LocalisationPatient
    from billing.models import Facture
    from pharmacy.models import PrescriptionPharmacie
    from laboratory.models import Analyse

    loc = LocalisationPatient.objects.filter(patient=patient).select_related('service').first()
    localisation = None
    if loc:
        localisation = {
            'batiment': loc.batiment,
            'etage': loc.etage,
            'salle': loc.salle,
            'latitude': float(loc.latitude) if loc.latitude else HOSPITAL_CENTER[0],
            'longitude': float(loc.longitude) if loc.longitude else HOSPITAL_CENTER[1],
            'statut': loc.statut,
            'statut_label': loc.get_statut_display(),
            'service_nom': loc.service.nom if loc.service else None,
        }

    rendez_vous = [
        {
            'id': r.id,
            'date_rdv': iso(r.date_rdv),
            'motif': r.motif,
            'statut': r.statut,
            'statut_label': r.get_statut_display(),
            'service_nom': r.service.nom if r.service else None,
            'medecin_nom': r.medecin.get_full_name() if r.medecin else None,
        }
        for r in RendezVous.objects.filter(patient=patient).select_related('medecin', 'service')
    ]

    consultations = [
        {
            'id': c.id,
            'motif_consultation': c.motif_consultation,
            'diagnostic': c.diagnostic,
            'notes_medicales': c.notes_medicales,
            'tension_arterielle': c.tension_arterielle,
            'temperature': float(c.temperature) if c.temperature else None,
            'poids': float(c.poids) if c.poids else None,
            'pouls': c.pouls,
            'date_consultation': iso(c.date_consultation),
            'medecin_nom': c.medecin.get_full_name() if c.medecin else None,
        }
        for c in Consultation.objects.filter(patient=patient).select_related('medecin')
    ]

    ordonnances = [
        {
            'id': o.id,
            'medicaments': o.medicaments,
            'instructions': o.instructions,
            'date_ordonnance': iso(o.date_ordonnance),
            'medecin_nom': o.medecin.get_full_name() if o.medecin else None,
        }
        for o in Ordonnance.objects.filter(patient=patient).select_related('medecin')
    ]

    analyses = [
        {
            'id': a.id,
            'examen_nom': a.examen_nom,
            'statut': a.statut,
            'resultat': a.resultat,
            'date_commande': iso(a.date_commande),
            'date_validation': iso(a.date_validation) if a.date_validation else None,
        }
        for a in Analyse.objects.filter(patient_dossier=patient)
    ]

    hospitalisations = [
        {
            'id': h.id,
            'motif_hospitalisation': h.motif_hospitalisation,
            'date_entree': iso(h.date_entree),
            'date_sortie': iso(h.date_sortie) if h.date_sortie else None,
            'frais_hebergement_total': float(h.frais_hebergement_total),
            'est_cloture': h.est_cloture,
            'chambre': f"Chambre {h.lit.chambre.numero} — Lit {h.lit.code_lit}" if h.lit else None,
        }
        for h in Admission.objects.filter(patient=patient).select_related('lit__chambre')
    ]

    factures = [
        {
            'id': f.id,
            'reference': f.reference,
            'montant_total_brut': float(f.montant_total_brut),
            'part_assurance': float(f.part_assurance),
            'montant_patient_net': float(f.montant_patient_net),
            'statut': f.statut,
            'date_facture': iso(f.date_facture),
        }
        for f in Facture.objects.filter(patient=patient)
    ]

    dispensations = [
        {
            'id': p.id,
            'medicament': p.medicament.nom,
            'quantite': p.quantite_delivree,
            'montant': float(p.frais_pharmacie_total),
            'est_paye': p.est_paye,
            'date_dispensation': iso(p.date_dispensation),
        }
        for p in PrescriptionPharmacie.objects.filter(patient=patient).select_related('medicament')
    ]

    return {
        'profil': _patient_out(patient),
        'localisation': localisation,
        'rendez_vous': rendez_vous,
        'consultations': consultations,
        'ordonnances': ordonnances,
        'analyses': analyses,
        'hospitalisations': hospitalisations,
        'factures': factures,
        'dispensations_pharmacie': dispensations,
    }


@admission_router.get("/patients/{patient_id}/dossier", tags=["Espace Patient"])
def dossier_patient_complet(request, patient_id: int):
    patient = get_object_or_404(Patient, id=patient_id)
    return _build_dossier_patient(patient)


# --- CLIENTS PRIVILÉGIÉS ---

class ClientPrivilegieCreateSchema(Schema):
    patient_id: int
    numero_carte: str
    type_carte: str = 'VIP'
    taux_reduction: int = 10
    date_expiration: Optional[date] = None
    notes: str = ''


class ClientPrivilegieOutSchema(Schema):
    id: int
    patient_id: int
    patient_nom: str
    numero_carte: str
    type_carte: str
    type_carte_label: str
    taux_reduction: int
    date_expiration: Optional[date] = None
    est_actif: bool
    notes: str


@admission_router.get("/clients-privilegies", response=List[ClientPrivilegieOutSchema], tags=["Clients Privilégiés"])
def lister_clients_privilegies(request):
    from .models import ClientPrivilegie
    return [
        {
            'id': c.id,
            'patient_id': c.patient_id,
            'patient_nom': f"{c.patient.nom} {c.patient.prenom}",
            'numero_carte': c.numero_carte,
            'type_carte': c.type_carte,
            'type_carte_label': c.get_type_carte_display(),
            'taux_reduction': c.taux_reduction,
            'date_expiration': c.date_expiration,
            'est_actif': c.est_actif,
            'notes': c.notes,
        }
        for c in ClientPrivilegie.objects.select_related('patient').all()
    ]


@admission_router.post("/clients-privilegies", response=ClientPrivilegieOutSchema, tags=["Clients Privilégiés"])
def creer_client_privilegie(request, data: ClientPrivilegieCreateSchema):
    from .models import ClientPrivilegie
    patient = get_object_or_404(Patient, id=data.patient_id)
    client = ClientPrivilegie.objects.create(
        patient=patient,
        numero_carte=data.numero_carte,
        type_carte=data.type_carte,
        taux_reduction=data.taux_reduction,
        date_expiration=data.date_expiration,
        notes=data.notes or '',
    )
    return {
        'id': client.id,
        'patient_id': client.patient_id,
        'patient_nom': f"{patient.nom} {patient.prenom}",
        'numero_carte': client.numero_carte,
        'type_carte': client.type_carte,
        'type_carte_label': client.get_type_carte_display(),
        'taux_reduction': client.taux_reduction,
        'date_expiration': client.date_expiration,
        'est_actif': client.est_actif,
        'notes': client.notes,
    }


@admission_router.patch("/clients-privilegies/{client_id}/toggle", response=ClientPrivilegieOutSchema, tags=["Clients Privilégiés"])
def toggle_client_privilegie(request, client_id: int):
    from .models import ClientPrivilegie
    client = get_object_or_404(ClientPrivilegie.objects.select_related('patient'), id=client_id)
    client.est_actif = not client.est_actif
    client.save(update_fields=['est_actif'])
    return {
        'id': client.id,
        'patient_id': client.patient_id,
        'patient_nom': f"{client.patient.nom} {client.patient.prenom}",
        'numero_carte': client.numero_carte,
        'type_carte': client.type_carte,
        'type_carte_label': client.get_type_carte_display(),
        'taux_reduction': client.taux_reduction,
        'date_expiration': client.date_expiration,
        'est_actif': client.est_actif,
        'notes': client.notes,
    }


# --- RENDEZ-VOUS & AGENDA ---

class RendezVousCreateSchema(Schema):
    patient_id: int
    medecin_id: Optional[int] = None
    service_id: Optional[int] = None
    date_rdv: str
    motif: str
    statut: str = 'PLANIFIE'
    notes: str = ''


class RendezVousUpdateSchema(Schema):
    date_rdv: Optional[str] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    medecin_id: Optional[int] = None


class RendezVousOutSchema(Schema):
    id: int
    patient_id: int
    patient_nom: str
    medecin_id: Optional[int] = None
    medecin_nom: Optional[str] = None
    service_id: Optional[int] = None
    service_nom: Optional[str] = None
    date_rdv: str
    motif: str
    statut: str
    statut_label: str
    notes: Optional[str] = None


def _rdv_out(r: RendezVous) -> dict:
    return {
        'id': r.id,
        'patient_id': r.patient_id,
        'patient_nom': f"{r.patient.nom} {r.patient.prenom}",
        'medecin_id': r.medecin_id,
        'medecin_nom': r.medecin.get_full_name() if r.medecin else None,
        'service_id': r.service_id,
        'service_nom': r.service.nom if r.service else None,
        'date_rdv': iso(r.date_rdv),
        'motif': r.motif,
        'statut': r.statut,
        'statut_label': r.get_statut_display(),
        'notes': r.notes,
    }


@admission_router.get("/rendez-vous", response=List[RendezVousOutSchema], tags=["Agenda & Rendez-vous"])
def lister_rendez_vous(request, medecin_id: int = None, service_id: int = None, patient_id: int = None):
    qs = RendezVous.objects.select_related('patient', 'medecin', 'service').order_by('date_rdv')
    if medecin_id:
        qs = qs.filter(medecin_id=medecin_id)
    if service_id:
        qs = qs.filter(service_id=service_id)
    if patient_id:
        qs = qs.filter(patient_id=patient_id)
    return [_rdv_out(r) for r in qs]


@admission_router.post("/rendez-vous", response=RendezVousOutSchema, tags=["Agenda & Rendez-vous"])
def creer_rendez_vous(request, data: RendezVousCreateSchema):
    from django.contrib.auth import get_user_model
    from clinical.models import Service
    User = get_user_model()
    patient = get_object_or_404(Patient, id=data.patient_id)
    from django.utils.dateparse import parse_datetime
    dt = parse_datetime(data.date_rdv.replace('Z', '+00:00') if data.date_rdv.endswith('Z') else data.date_rdv)
    if not dt:
        from ninja.errors import HttpError
        raise HttpError(400, 'Date/heure invalide')
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    rdv = RendezVous(
        patient=patient,
        motif=data.motif,
        statut=data.statut,
        notes=data.notes or '',
        date_rdv=dt,
    )
    if data.medecin_id:
        rdv.medecin = get_object_or_404(User, id=data.medecin_id)
    if data.service_id:
        rdv.service = get_object_or_404(Service, id=data.service_id)
    rdv.save()
    return _rdv_out(rdv)


@admission_router.patch("/rendez-vous/{rdv_id}", response=RendezVousOutSchema, tags=["Agenda & Rendez-vous"])
def modifier_rendez_vous(request, rdv_id: int, data: RendezVousUpdateSchema):
    rdv = get_object_or_404(RendezVous.objects.select_related('patient', 'medecin', 'service'), id=rdv_id)
    payload = {k: v for k, v in data.dict().items() if v is not None}
    if 'medecin_id' in payload:
        from django.contrib.auth import get_user_model
        mid = payload.pop('medecin_id')
        rdv.medecin = get_object_or_404(get_user_model(), id=mid) if mid else None
    for k, v in payload.items():
        setattr(rdv, k, v)
    rdv.save()
    return _rdv_out(rdv)


@admission_router.delete("/rendez-vous/{rdv_id}", tags=["Agenda & Rendez-vous"])
def supprimer_rendez_vous(request, rdv_id: int):
    get_object_or_404(RendezVous, id=rdv_id).delete()
    return {"success": True}


@admission_router.get("/agenda/medecin/{medecin_id}/patients", tags=["Agenda & Rendez-vous"])
def patients_du_medecin(request, medecin_id: int):
    """Patients ayant au moins un RDV ou une consultation avec ce médecin."""
    from consultation.models import Consultation
    from django.contrib.auth import get_user_model
    medecin = get_object_or_404(get_user_model(), id=medecin_id)
    patient_ids = set(
        RendezVous.objects.filter(medecin=medecin).values_list('patient_id', flat=True)
    )
    patient_ids.update(
        Consultation.objects.filter(medecin=medecin).values_list('patient_id', flat=True)
    )
    patients = Patient.objects.filter(id__in=patient_ids).order_by('nom', 'prenom')
    return [_patient_out(p) for p in patients]


# --- NOTES PATIENT (secrétariat) ---

class NotePatientCreateSchema(Schema):
    contenu: str
    medecin_id: Optional[int] = None
    est_important: bool = False


class NotePatientOutSchema(Schema):
    id: int
    patient_id: int
    patient_nom: str
    auteur_nom: Optional[str] = None
    medecin_nom: Optional[str] = None
    contenu: str
    est_important: bool
    date_creation: str


@admission_router.get("/patients/{patient_id}/notes", response=List[NotePatientOutSchema], tags=["Notes patient"])
def lister_notes_patient(request, patient_id: int, medecin_id: int = None):
    patient = get_object_or_404(Patient, id=patient_id)
    qs = NotePatient.objects.filter(patient=patient).select_related('auteur', 'medecin')
    if medecin_id:
        qs = qs.filter(medecin_id=medecin_id)
    return [
        {
            'id': n.id,
            'patient_id': n.patient_id,
            'patient_nom': f"{patient.nom} {patient.prenom}",
            'auteur_nom': n.auteur.get_full_name() if n.auteur else None,
            'medecin_nom': n.medecin.get_full_name() if n.medecin else None,
            'contenu': n.contenu,
            'est_important': n.est_important,
            'date_creation': iso(n.date_creation),
        }
        for n in qs
    ]


@admission_router.post("/patients/{patient_id}/notes", response=NotePatientOutSchema, tags=["Notes patient"])
def ajouter_note_patient(request, patient_id: int, data: NotePatientCreateSchema):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    patient = get_object_or_404(Patient, id=patient_id)
    auteur = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
    medecin = None
    if data.medecin_id:
        medecin = get_object_or_404(User, id=data.medecin_id, role='MEDECIN')
    note = NotePatient.objects.create(
        patient=patient,
        auteur=auteur,
        medecin=medecin,
        contenu=data.contenu,
        est_important=data.est_important,
    )
    return {
        'id': note.id,
        'patient_id': note.patient_id,
        'patient_nom': f"{patient.nom} {patient.prenom}",
        'auteur_nom': auteur.get_full_name() if auteur else 'Secrétariat',
        'medecin_nom': medecin.get_full_name() if medecin else None,
        'contenu': note.contenu,
        'est_important': note.est_important,
        'date_creation': iso(note.date_creation),
    }


# --- CHAT PATIENT ↔ ÉQUIPE MÉDICALE ---

STAFF_CHAT_ROLES = {
    'ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE',
}


class _ChatPatientUser:
    """Accès chat pour patient connecté par nom (session portail, sans compte OTP)."""

    def __init__(self, patient: Patient):
        self.patient = patient
        self.role = 'PATIENT'
        self.email = (patient.email or f'patient-{patient.id}@portail.sghl').lower()
        self.username = f'{patient.nom}.{patient.prenom}'.lower()

    def get_full_name(self):
        return f'{self.patient.nom} {self.patient.prenom}'.strip()


def _chat_user(request):
    from config.auth_helpers import get_api_user
    user = get_api_user(request)
    if user:
        return user
    pid = (request.headers.get('X-SGHL-Patient-Id') or '').strip()
    nom = (request.headers.get('X-SGHL-Patient-Nom') or '').strip()
    if not pid.isdigit():
        return None
    patient = Patient.objects.filter(id=int(pid)).first()
    if not patient or not _name_matches_patient(nom, patient):
        return None
    return _ChatPatientUser(patient)


def _patient_for_user(user):
    if not user:
        return None
    if isinstance(user, _ChatPatientUser):
        return user.patient
    if user.role == 'PATIENT':
        p = Patient.objects.filter(user=user).first()
        if p:
            return p
        return _resolve_patient_by_email(user.email)
    return None


def _require_chat_access(request, patient_id: int):
    from ninja.errors import HttpError
    user = _chat_user(request)
    if not user:
        raise HttpError(401, 'Connexion requise pour accéder au chat.')
    patient = get_object_or_404(Patient, id=patient_id)
    if user.role in STAFF_CHAT_ROLES:
        return user, patient
    own = _patient_for_user(user)
    if own and own.id == patient.id:
        return user, patient
    raise HttpError(403, 'Accès refusé à cette conversation.')


def _chat_out(m: PatientChatMessage) -> dict:
    return {
        'id': m.id,
        'patient_id': m.patient_id,
        'patient_nom': f"{m.patient.nom} {m.patient.prenom}",
        'sender_email': m.sender_email,
        'sender_name': m.sender_name,
        'sender_role': m.sender_role,
        'message_type': m.message_type,
        'message_type_label': m.get_message_type_display(),
        'contenu': m.contenu,
        'rendez_vous_id': m.rendez_vous_id,
        'metadata': m.metadata or {},
        'lu_par_patient': m.lu_par_patient,
        'lu_par_equipe': m.lu_par_equipe,
        'created_at': iso(m.created_at),
        'is_mine': False,
    }


class ChatMessageCreateSchema(Schema):
    patient_id: int
    contenu: str


class ChatRdvDemandeSchema(Schema):
    patient_id: int
    date_rdv: str
    motif: str
    service_id: Optional[int] = None
    message: str = ''


class ChatInboxSchema(Schema):
    patient_id: int
    patient_nom: str
    sgl_id: str
    dernier_message: str
    dernier_type: str
    created_at: str
    non_lus_equipe: int


@admission_router.get('/chat/inbox', response=List[ChatInboxSchema], tags=['Chat médical'])
def chat_inbox(request):
    from ninja.errors import HttpError
    from django.db.models import Count, Max, Q
    user = _chat_user(request)
    if not user or user.role not in STAFF_CHAT_ROLES:
        raise HttpError(403, 'Réservé au personnel médical.')

    latest_ids = (
        PatientChatMessage.objects.values('patient_id')
        .annotate(last_id=Max('id'))
        .values_list('last_id', flat=True)
    )
    messages = PatientChatMessage.objects.filter(id__in=latest_ids).select_related('patient')
    unread = dict(
        PatientChatMessage.objects.filter(lu_par_equipe=False, sender_role='PATIENT')
        .values('patient_id')
        .annotate(c=Count('id'))
        .values_list('patient_id', 'c')
    )
    items = []
    for m in messages.order_by('-created_at')[:80]:
        items.append({
            'patient_id': m.patient_id,
            'patient_nom': f"{m.patient.nom} {m.patient.prenom}",
            'sgl_id': m.patient.sgl_id,
            'dernier_message': m.contenu[:200],
            'dernier_type': m.message_type,
            'created_at': iso(m.created_at),
            'non_lus_equipe': unread.get(m.patient_id, 0),
        })
    return items


@admission_router.get('/chat/messages', tags=['Chat médical'])
def lister_messages_chat(request, patient_id: int, limit: int = 100):
    user, patient = _require_chat_access(request, patient_id)
    qs = PatientChatMessage.objects.filter(patient=patient).select_related('patient').order_by('created_at')[:min(limit, 300)]
    out = []
    for m in qs:
        row = _chat_out(m)
        row['is_mine'] = m.sender_email.lower() == user.email.lower()
        out.append(row)

    if user.role in STAFF_CHAT_ROLES:
        PatientChatMessage.objects.filter(patient=patient, sender_role='PATIENT', lu_par_equipe=False).update(lu_par_equipe=True)
    else:
        PatientChatMessage.objects.filter(patient=patient).exclude(sender_role='PATIENT').filter(lu_par_patient=False).update(lu_par_patient=True)

    return out


@admission_router.post('/chat/messages', tags=['Chat médical'])
def envoyer_message_chat(request, data: ChatMessageCreateSchema):
    from ninja.errors import HttpError
    user, patient = _require_chat_access(request, data.patient_id)
    contenu = (data.contenu or '').strip()
    if not contenu:
        raise HttpError(400, 'Message vide.')
    if len(contenu) > 4000:
        raise HttpError(400, 'Message trop long (4000 caractères max).')

    role = user.role if user.role != 'PATIENT' else 'PATIENT'
    name = user.get_full_name() or user.username or user.email.split('@')[0]
    msg = PatientChatMessage.objects.create(
        patient=patient,
        sender_email=user.email,
        sender_name=name,
        sender_role=role,
        message_type='CHAT',
        contenu=contenu,
        lu_par_equipe=role != 'PATIENT',
        lu_par_patient=role == 'PATIENT',
    )
    if role == 'PATIENT':
        try:
            from core.models import Notification
            Notification.objects.create(
                user=None,
                title=f'Message patient — {patient.nom} {patient.prenom}',
                message=contenu[:500],
                level='INFO',
                link='/patients',
            )
        except Exception:
            pass
    row = _chat_out(msg)
    row['is_mine'] = True
    return row


@admission_router.post('/chat/rdv-demande', tags=['Chat médical'])
def demander_rdv_via_chat(request, data: ChatRdvDemandeSchema):
    from ninja.errors import HttpError
    from django.contrib.auth import get_user_model
    from clinical.models import Service
    from django.utils.dateparse import parse_datetime

    user, patient = _require_chat_access(request, data.patient_id)
    motif = (data.motif or '').strip()
    if not motif:
        raise HttpError(400, 'Indiquez le motif du rendez-vous.')

    dt = parse_datetime(data.date_rdv.replace('Z', '+00:00') if data.date_rdv.endswith('Z') else data.date_rdv)
    if not dt:
        raise HttpError(400, 'Date/heure invalide.')
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)

    rdv = RendezVous(patient=patient, motif=motif, statut='PLANIFIE', date_rdv=dt)
    if data.service_id:
        rdv.service = get_object_or_404(Service, id=data.service_id)
    rdv.save()

    extra = (data.message or '').strip()
    contenu = (
        f"📅 Demande de rendez-vous — {dt.strftime('%d/%m/%Y à %H:%M')}\n"
        f"Motif : {motif}"
    )
    if extra:
        contenu += f"\n\nMessage : {extra}"

    name = user.get_full_name() or user.username or user.email.split('@')[0]
    msg = PatientChatMessage.objects.create(
        patient=patient,
        sender_email=user.email,
        sender_name=name,
        sender_role=user.role,
        message_type='RDV_DEMANDE',
        contenu=contenu,
        rendez_vous=rdv,
        metadata={
            'date_rdv': iso(dt),
            'motif': motif,
            'service_id': data.service_id,
            'rdv_id': rdv.id,
        },
        lu_par_equipe=False,
        lu_par_patient=True,
    )

    try:
        from core.models import Notification
        Notification.objects.create(
            user=None,
            title=f'RDV demandé — {patient.nom} {patient.prenom}',
            message=contenu[:500],
            level='INFO',
            link='/patients',
        )
    except Exception:
        pass

    row = _chat_out(msg)
    row['is_mine'] = True
    return {'message': row, 'rendez_vous': _rdv_out(rdv)}


@admission_router.get('/chat/unread-count', tags=['Chat médical'])
def chat_unread_count(request, patient_id: int = None):
    from ninja.errors import HttpError
    user = _chat_user(request)
    if not user:
        raise HttpError(401, 'Connexion requise.')

    if user.role in STAFF_CHAT_ROLES:
        if patient_id:
            c = PatientChatMessage.objects.filter(
                patient_id=patient_id, sender_role='PATIENT', lu_par_equipe=False,
            ).count()
        else:
            c = PatientChatMessage.objects.filter(sender_role='PATIENT', lu_par_equipe=False).count()
        return {'count': c, 'role': 'staff'}

    own = _patient_for_user(user)
    if not own:
        return {'count': 0, 'role': 'patient'}
    c = PatientChatMessage.objects.filter(
        patient=own, lu_par_patient=False,
    ).exclude(sender_role='PATIENT').count()
    return {'count': c, 'role': 'patient', 'patient_id': own.id}


@admission_router.delete('/chat/conversation', tags=['Chat médical'])
def supprimer_conversation_chat(request, patient_id: int):
    from ninja.errors import HttpError

    user, patient = _require_chat_access(request, patient_id)
    deleted, _ = PatientChatMessage.objects.filter(patient=patient).delete()
    if deleted == 0:
        raise HttpError(404, 'Aucune conversation à supprimer.')
    return {
        'success': True,
        'deleted': deleted,
        'patient_id': patient.id,
        'detail': 'Conversation supprimée.',
    }
