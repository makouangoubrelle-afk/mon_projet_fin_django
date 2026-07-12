from ninja import Router, Schema
from typing import List, Optional
from decimal import Decimal
from django.shortcuts import get_object_or_404
from config.serializers import iso
from .models import Analyse
from admission.models import Patient

lab_router = Router()


class AnalyseCreateSchema(Schema):
    patient_id: int
    examen_nom: str
    resultat: str = None


class AnalyseUpdateSchema(Schema):
    examen_nom: Optional[str] = None
    resultat: Optional[str] = None
    statut: Optional[str] = None


@lab_router.get("/analyses")
def liste_analyses(request, patient_id: int = None):
    qs = Analyse.objects.select_related('patient_dossier').order_by('-date_commande')
    if patient_id:
        qs = qs.filter(patient_dossier_id=patient_id)
    result = []
    for a in qs:
        result.append({
            'id': a.id,
            'examen_nom': a.examen_nom,
            'statut': a.statut,
            'resultat': a.resultat,
            'date_commande': iso(a.date_commande),
            'date_validation': iso(a.date_validation) if a.date_validation else None,
            'patient_id': a.patient_dossier_id,
            'patient_nom': f"{a.patient_dossier.nom} {a.patient_dossier.prenom}" if a.patient_dossier else None,
            'patient_qr_code': str(a.patient_dossier.qr_code) if a.patient_dossier else None,
        })
    return result


@lab_router.post("/analyses")
def creer_analyse(request, data: AnalyseCreateSchema):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    patient = get_object_or_404(Patient, id=data.patient_id)
    user = patient.user or User.objects.first()
    analyse = Analyse.objects.create(
        patient=user, patient_dossier=patient,
        examen_nom=data.examen_nom, resultat=data.resultat,
    )
    return {'id': analyse.id, 'examen_nom': analyse.examen_nom, 'statut': analyse.statut}


@lab_router.put("/analyses/{analyse_id}")
def modifier_analyse(request, analyse_id: int, data: AnalyseUpdateSchema):
    analyse = get_object_or_404(Analyse, id=analyse_id)
    for k, v in {k: v for k, v in data.dict().items() if v is not None}.items():
        setattr(analyse, k, v)
    analyse.save()
    return {'id': analyse.id, 'statut': analyse.statut}


@lab_router.delete("/analyses/{analyse_id}")
def supprimer_analyse(request, analyse_id: int):
    get_object_or_404(Analyse, id=analyse_id).delete()
    return {"success": True}


@lab_router.post("/analyses/{analyse_id}/valider", tags=["Laboratoire"])
def valider_analyse(request, analyse_id: int):
    from django.utils import timezone
    analyse = get_object_or_404(Analyse, id=analyse_id)
    analyse.statut = 'VALIDE'
    if hasattr(request, 'user') and not request.user.is_anonymous:
        analyse.valide_par = request.user
    analyse.date_validation = timezone.now()
    analyse.save()
    return {"message": "Analyse validée et verrouillée"}
