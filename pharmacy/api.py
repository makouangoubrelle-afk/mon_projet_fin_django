from ninja import Router, Schema
from typing import List, Optional
from decimal import Decimal
from django.shortcuts import get_object_or_404
from .models import Medicament, PrescriptionPharmacie
from admission.models import Patient

pharmacy_router = Router()


class MedicamentSchema(Schema):
    id: int
    nom: str
    quantite_en_stock: int
    prix_unitaire: Decimal


class MedicamentCreateSchema(Schema):
    nom: str
    code_barre: str = None
    quantite_en_stock: int = 0
    prix_unitaire: float


class MedicamentUpdateSchema(Schema):
    nom: Optional[str] = None
    quantite_en_stock: Optional[int] = None
    prix_unitaire: Optional[float] = None


class PrescriptionCreateSchema(Schema):
    patient_id: int
    medicament_id: int
    quantite_delivree: int


@pharmacy_router.post("/medicaments", response=MedicamentSchema, tags=["Gestion de la Pharmacie"])
def ajouter_medicament(request, data: MedicamentCreateSchema):
    return Medicament.objects.create(**data.dict())


@pharmacy_router.get("/medicaments", response=List[MedicamentSchema], tags=["Gestion de la Pharmacie"])
def lister_medicaments(request):
    return Medicament.objects.all()


@pharmacy_router.put("/medicaments/{med_id}", response=MedicamentSchema, tags=["Gestion de la Pharmacie"])
def modifier_medicament(request, med_id: int, data: MedicamentUpdateSchema):
    med = get_object_or_404(Medicament, id=med_id)
    for k, v in {k: v for k, v in data.dict().items() if v is not None}.items():
        setattr(med, k, v)
    med.save()
    return med


@pharmacy_router.delete("/medicaments/{med_id}", tags=["Gestion de la Pharmacie"])
def supprimer_medicament(request, med_id: int):
    get_object_or_404(Medicament, id=med_id).delete()
    return {"success": True}


@pharmacy_router.post("/dispensation", tags=["Gestion de la Pharmacie"])
def dispenser_medicament(request, data: PrescriptionCreateSchema):
    medicament = get_object_or_404(Medicament, id=data.medicament_id)
    patient = get_object_or_404(Patient, id=data.patient_id)
    if medicament.quantite_en_stock < data.quantite_delivree:
        from ninja.errors import HttpError
        raise HttpError(400, "Stock insuffisant.")
    medicament.quantite_en_stock -= data.quantite_delivree
    medicament.save()
    prescription = PrescriptionPharmacie.objects.create(
        patient=patient, medicament=medicament, quantite_delivree=data.quantite_delivree,
    )
    return {'id': prescription.id, 'montant': float(prescription.frais_pharmacie_total)}
