from ninja import Router, Schema
from typing import List, Optional
from decimal import Decimal
from django.shortcuts import get_object_or_404
from config.serializers import iso
from .models import Consultation, Ordonnance
from admission.models import Patient

consultation_router = Router()


class ConsultationCreateSchema(Schema):
    patient_id: int
    tension_arterielle: str = None
    temperature: float = None
    poids: float = None
    pouls: int = None
    motif_consultation: str
    diagnostic: str = None
    notes_medicales: str = None
    frais_consultation: float = 10000.00


class ConsultationOutSchema(Schema):
    id: int
    patient_id: int
    medecin_id: Optional[int] = None
    motif_consultation: str
    diagnostic: Optional[str] = None
    frais_consultation: Decimal
    date_consultation: str


class OrdonnanceCreateSchema(Schema):
    patient_id: int
    medicaments: str
    instructions: str = None
    consultation_id: int = None
    medecin_id: Optional[int] = None


class OrdonnanceOutSchema(Schema):
    id: int
    patient_id: int
    patient_nom: str
    patient_qr_code: Optional[str] = None
    medecin_nom: Optional[str] = None
    medicaments: str
    instructions: Optional[str] = None
    date_ordonnance: str


def _consultation_out(c: Consultation) -> dict:
    return {
        'id': c.id,
        'patient_id': c.patient_id,
        'medecin_id': c.medecin_id,
        'motif_consultation': c.motif_consultation,
        'diagnostic': c.diagnostic,
        'frais_consultation': c.frais_consultation,
        'date_consultation': iso(c.date_consultation),
    }


def _ordonnance_out(o: Ordonnance) -> dict:
    return {
        'id': o.id,
        'patient_id': o.patient_id,
        'patient_nom': f"{o.patient.nom} {o.patient.prenom}",
        'patient_qr_code': str(o.patient.qr_code),
        'medecin_nom': o.medecin.get_full_name() if o.medecin else None,
        'medicaments': o.medicaments,
        'instructions': o.instructions,
        'date_ordonnance': iso(o.date_ordonnance),
    }


@consultation_router.get("/", response=List[ConsultationOutSchema], tags=["Espace Médical & Consultations"])
def lister_consultations(request):
    return [_consultation_out(c) for c in Consultation.objects.all().order_by('-date_consultation')]


@consultation_router.post("/", response=ConsultationOutSchema, tags=["Espace Médical & Consultations"])
def creer_consultation(request, data: ConsultationCreateSchema):
    payload = data.dict()
    patient_id = payload.pop("patient_id")

    patient = Patient.objects.get(id=patient_id)
    consultation = Consultation(**payload, patient=patient)

    if request.user and request.user.is_authenticated:
        consultation.medecin = request.user

    consultation.save()
    return _consultation_out(consultation)


@consultation_router.get("/patient/{patient_id}", response=List[ConsultationOutSchema], tags=["Espace Médical & Consultations"])
def historique_patient(request, patient_id: int):
    qs = Consultation.objects.filter(patient_id=patient_id).order_by('-date_consultation')
    return [_consultation_out(c) for c in qs]


@consultation_router.get("/ordonnances", response=List[OrdonnanceOutSchema], tags=["Ordonnances"])
def lister_ordonnances(request, patient_id: int = None):
    qs = Ordonnance.objects.select_related('patient', 'medecin').order_by('-date_ordonnance')
    if patient_id:
        qs = qs.filter(patient_id=patient_id)
    return [_ordonnance_out(o) for o in qs]


@consultation_router.get("/ordonnances/{ordonnance_id}", response=OrdonnanceOutSchema, tags=["Ordonnances"])
def detail_ordonnance(request, ordonnance_id: int):
    o = Ordonnance.objects.select_related('patient', 'medecin').get(id=ordonnance_id)
    return _ordonnance_out(o)


@consultation_router.post("/ordonnances", response=OrdonnanceOutSchema, tags=["Ordonnances"])
def creer_ordonnance(request, data: OrdonnanceCreateSchema):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    patient = get_object_or_404(Patient, id=data.patient_id)
    ordonnance = Ordonnance(
        patient=patient,
        medicaments=data.medicaments,
        instructions=data.instructions or '',
    )
    if data.consultation_id:
        ordonnance.consultation_id = data.consultation_id
    if data.medecin_id:
        ordonnance.medecin = get_object_or_404(User, id=data.medecin_id, role='MEDECIN')
    elif request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'MEDECIN':
        ordonnance.medecin = request.user
    ordonnance.save()
    return _ordonnance_out(ordonnance)
