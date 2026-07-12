from ninja import Router, Schema
from typing import List, Optional
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.utils import timezone
from config.serializers import iso
from .models import Facture, LigneFacture, Paiement, CompteBanque, MouvementBanque
from admission.models import Patient
from pharmacy.models import PrescriptionPharmacie

billing_router = Router()


class LigneFactureSchema(Schema):
    service: str
    montant: float


class FactureCreateSchema(Schema):
    patient_id: int
    societe: str = ''
    lignes: List[LigneFactureSchema] = []


class PaiementCreateSchema(Schema):
    montant: float
    mode_paiement: str
    reference_transaction: str = ''
    compte_banque_id: Optional[int] = None


class FactureOutSchema(Schema):
    id: int
    reference: str
    patient_id: int
    patient_nom: str = ''
    societe: str
    montant_consultations: Decimal
    montant_hospitalisation: Decimal
    montant_pharmacie: Decimal
    montant_services: Decimal
    montant_total_brut: Decimal
    part_assurance: Decimal
    reduction_privilege: Decimal
    montant_patient_net: Decimal
    montant_paye: Decimal
    montant_reste: Decimal
    statut: str
    date_facture: str
    lignes: List[dict] = []
    paiements: List[dict] = []


class CompteBanqueOutSchema(Schema):
    id: int
    nom: str
    numero_compte: str
    banque: str
    solde: Decimal
    devise: str
    est_actif: bool


class CompteBanqueCreateSchema(Schema):
    nom: str
    numero_compte: str
    banque: str = 'Rawbank'
    solde: float = 0
    devise: str = 'CDF'


class MouvementOutSchema(Schema):
    id: int
    compte_id: int
    type_mouvement: str
    montant: Decimal
    libelle: str
    date_mouvement: str


def _facture_out(f: Facture) -> dict:
    patient = f.patient
    return {
        'id': f.id,
        'reference': f.reference,
        'patient_id': f.patient_id,
        'patient_nom': f"{patient.nom} {patient.prenom}",
        'societe': f.societe,
        'montant_consultations': f.montant_consultations,
        'montant_hospitalisation': f.montant_hospitalisation,
        'montant_pharmacie': f.montant_pharmacie,
        'montant_services': f.montant_services,
        'montant_total_brut': f.montant_total_brut,
        'part_assurance': f.part_assurance,
        'reduction_privilege': f.reduction_privilege,
        'montant_patient_net': f.montant_patient_net,
        'montant_paye': f.montant_paye,
        'montant_reste': f.montant_reste,
        'statut': f.statut,
        'date_facture': iso(f.date_facture),
        'lignes': [
            {'id': l.id, 'service': l.service, 'montant': float(l.montant), 'ordre': l.ordre}
            for l in f.lignes.all()
        ],
        'paiements': [
            {
                'id': p.id,
                'montant': float(p.montant),
                'mode_paiement': p.mode_paiement,
                'mode_label': p.get_mode_paiement_display(),
                'reference_transaction': p.reference_transaction,
                'date_paiement': iso(p.date_paiement),
            }
            for p in f.paiements.all()
        ],
    }


@billing_router.get("/factures", response=List[FactureOutSchema], tags=["Gestion de la Caisse & Facturation"])
def lister_factures(request):
    qs = Facture.objects.select_related('patient').prefetch_related('lignes', 'paiements').order_by('-date_facture')
    return [_facture_out(f) for f in qs]


@billing_router.get("/factures/patient/{patient_id}", response=List[FactureOutSchema], tags=["Gestion de la Caisse & Facturation"])
def factures_patient(request, patient_id: int):
    qs = Facture.objects.filter(patient_id=patient_id).select_related('patient').prefetch_related('lignes', 'paiements')
    return [_facture_out(f) for f in qs.order_by('-date_facture')]


@billing_router.post("/factures", response=FactureOutSchema, tags=["Gestion de la Caisse & Facturation"])
def creer_facture(request, data: FactureCreateSchema):
    patient = get_object_or_404(Patient, id=data.patient_id)
    facture = Facture.objects.create(patient=patient, societe=data.societe or '')
    for i, ligne in enumerate(data.lignes, start=1):
        if ligne.service and ligne.montant:
            LigneFacture.objects.create(
                facture=facture, service=ligne.service, montant=ligne.montant, ordre=i,
            )
    facture.calculer_facture()
    facture.save()
    return _facture_out(facture)


@billing_router.post("/factures/patient/{patient_id}", response=FactureOutSchema, tags=["Gestion de la Caisse & Facturation"])
def generer_facture_patient(request, patient_id: int):
    patient = get_object_or_404(Patient, id=patient_id)
    facture = Facture.objects.filter(patient=patient, statut='EN_ATTENTE').first()
    if not facture:
        facture = Facture(patient=patient)
    facture.calculer_facture()
    facture.save()
    return _facture_out(facture)


@billing_router.get("/paiements", tags=["Gestion de la Caisse & Facturation"])
def lister_paiements(request):
    qs = Paiement.objects.select_related('facture', 'facture__patient').order_by('-date_paiement')[:200]
    return [
        {
            'id': p.id,
            'facture_id': p.facture_id,
            'facture_reference': p.facture.reference,
            'patient_nom': f'{p.facture.patient.nom} {p.facture.patient.prenom}',
            'montant': float(p.montant),
            'mode_paiement': p.mode_paiement,
            'mode_label': p.get_mode_paiement_display(),
            'reference_transaction': p.reference_transaction,
            'date_paiement': iso(p.date_paiement),
        }
        for p in qs
    ]


@billing_router.post("/factures/{facture_id}/paiement", response=FactureOutSchema, tags=["Gestion de la Caisse & Facturation"])
def enregistrer_paiement(request, facture_id: int, data: PaiementCreateSchema):
    modes_valides = {m[0] for m in Paiement.MODE_CHOICES}
    if data.mode_paiement not in modes_valides:
        from ninja.errors import HttpError
        raise HttpError(400, f"Mode invalide. Choix : {', '.join(modes_valides)}")

    facture = get_object_or_404(Facture.objects.select_related('patient'), id=facture_id)
    montant = Decimal(str(data.montant))

    paiement = Paiement.objects.create(
        facture=facture,
        montant=montant,
        mode_paiement=data.mode_paiement,
        reference_transaction=data.reference_transaction or '',
    )

    facture.montant_paye += montant
    facture.calculer_facture()
    facture.save()

    if facture.statut == 'PAYE':
        PrescriptionPharmacie.objects.filter(patient=facture.patient, est_paye=False).update(est_paye=True)

    from core.services import log_activity
    log_activity(request, 'Paiement enregistré', 'Facturation', f'{facture.reference} — {montant} {data.mode_paiement}')

    if data.compte_banque_id:
        compte = get_object_or_404(CompteBanque, id=data.compte_banque_id)
        compte.solde += montant
        compte.save(update_fields=['solde'])
        MouvementBanque.objects.create(
            compte=compte,
            type_mouvement='ENTREE',
            montant=montant,
            libelle=f"Paiement {paiement.get_mode_paiement_display()} — {facture.reference}",
            facture=facture,
        )

    return _facture_out(facture)


@billing_router.post("/factures/{facture_id}/payer", response=FactureOutSchema, tags=["Gestion de la Caisse & Facturation"])
def encaisser_facture(request, facture_id: int):
    facture = get_object_or_404(Facture, id=facture_id)
    reste = facture.montant_reste or facture.montant_patient_net
    return enregistrer_paiement(request, facture_id, PaiementCreateSchema(
        montant=float(reste), mode_paiement='ESPECES',
    ))


# --- BANQUE ---

@billing_router.get("/banque/comptes", response=List[CompteBanqueOutSchema], tags=["Banque"])
def lister_comptes(request):
    return list(CompteBanque.objects.filter(est_actif=True).order_by('banque'))


@billing_router.post("/banque/comptes", response=CompteBanqueOutSchema, tags=["Banque"])
def creer_compte(request, data: CompteBanqueCreateSchema):
    return CompteBanque.objects.create(**data.dict())


@billing_router.get("/banque/mouvements", response=List[MouvementOutSchema], tags=["Banque"])
def lister_mouvements(request):
    return [
        {
            'id': m.id,
            'compte_id': m.compte_id,
            'type_mouvement': m.type_mouvement,
            'montant': m.montant,
            'libelle': m.libelle,
            'date_mouvement': iso(m.date_mouvement),
        }
        for m in MouvementBanque.objects.select_related('compte').order_by('-date_mouvement')[:100]
    ]


@billing_router.get("/banque/solde-total", tags=["Banque"])
def solde_total(request):
    comptes = CompteBanque.objects.filter(est_actif=True)
    total = sum(c.solde for c in comptes)
    entrees = MouvementBanque.objects.filter(type_mouvement='ENTREE').count()
    return {
        'solde_total': float(total),
        'nb_comptes': comptes.count(),
        'nb_entrees': entrees,
        'devise': 'CDF',
    }
