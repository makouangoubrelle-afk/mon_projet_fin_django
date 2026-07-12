from django.db import models
from decimal import Decimal
from admission.models import Patient
from consultation.models import Consultation
from clinical.models import Admission
from pharmacy.models import PrescriptionPharmacie


class Facture(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de paiement'),
        ('PAYE', 'Payée'),
        ('PARTIEL', 'Paiement Partiel'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="factures")
    reference = models.CharField(max_length=30, unique=True, blank=True)
    societe = models.CharField(max_length=100, blank=True, default='')
    date_facture = models.DateTimeField(auto_now_add=True)
    montant_consultations = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    montant_laboratoire = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    montant_hospitalisation = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    montant_pharmacie = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    montant_services = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    montant_total_brut = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    part_assurance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    reduction_privilege = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    montant_patient_net = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    montant_reste = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')

    def calculer_facture(self):
        consultations = Consultation.objects.filter(patient=self.patient)
        self.montant_consultations = sum((Decimal(str(c.frais_consultation)) for c in consultations), Decimal(0))
        admissions = Admission.objects.filter(patient=self.patient, est_cloture=True)
        self.montant_hospitalisation = sum((Decimal(str(a.frais_hebergement_total)) for a in admissions), Decimal(0))
        achats = PrescriptionPharmacie.objects.filter(patient=self.patient, est_paye=False)
        self.montant_pharmacie = sum((Decimal(str(p.frais_pharmacie_total)) for p in achats), Decimal(0))
        if self.pk:
            lignes = self.lignes.all()
            self.montant_services = sum((Decimal(str(l.montant)) for l in lignes), Decimal(0))
        else:
            self.montant_services = Decimal(0.00)
        self.montant_total_brut = (
            Decimal(self.montant_consultations) + Decimal(self.montant_hospitalisation)
            + Decimal(self.montant_pharmacie) + Decimal(self.montant_laboratoire) + Decimal(self.montant_services)
        )
        if self.patient.assurance:
            taux = Decimal(self.patient.assurance.taux_couverture) / Decimal(100)
            self.part_assurance = self.montant_total_brut * taux
        else:
            self.part_assurance = Decimal(0.00)
        net_avant_reduction = self.montant_total_brut - self.part_assurance
        self.reduction_privilege = Decimal(0.00)
        if hasattr(self.patient, 'privilege') and self.patient.privilege.est_actif:
            taux_red = Decimal(self.patient.privilege.taux_reduction) / Decimal(100)
            self.reduction_privilege = net_avant_reduction * taux_red
        self.montant_patient_net = net_avant_reduction - self.reduction_privilege
        montant_paye = Decimal(str(self.montant_paye or 0))
        self.montant_reste = self.montant_patient_net - montant_paye
        if self.montant_reste <= 0 and self.montant_patient_net > 0:
            self.statut = 'PAYE'
            self.montant_reste = Decimal(0.00)
        elif montant_paye > 0 and self.montant_reste > 0:
            self.statut = 'PARTIEL'

    def save(self, *args, **kwargs):
        if not self.reference:
            from django.utils import timezone
            year = timezone.now().year
            count = Facture.objects.filter(reference__startswith=f'FAC-{year}').count() + 1
            self.reference = f'FAC-{year}-{count:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Facture {self.reference} - {self.patient.nom}"


class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    service = models.CharField(max_length=200)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    ordre = models.IntegerField(default=1)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"{self.service} — {self.montant}"


class Paiement(models.Model):
    MODE_CHOICES = [
        ('CARTE', 'Par carte'),
        ('MOMO', 'Par MoMo'),
        ('AIRTEL', 'Par Airtel Money'),
        ('MTN', 'Par MTN Mobile Money'),
        ('ESPECES', 'Espèces'),
    ]
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    mode_paiement = models.CharField(max_length=10, choices=MODE_CHOICES)
    reference_transaction = models.CharField(max_length=50, blank=True, default='')
    date_paiement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_mode_paiement_display()} — {self.montant}"


class CompteBanque(models.Model):
    nom = models.CharField(max_length=100)
    numero_compte = models.CharField(max_length=50)
    banque = models.CharField(max_length=100, default='Rawbank')
    solde = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    devise = models.CharField(max_length=5, default='CDF')
    est_actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.banque} — {self.nom} ({self.solde} {self.devise})"


class MouvementBanque(models.Model):
    TYPE_CHOICES = [('ENTREE', 'Entrée'), ('SORTIE', 'Sortie')]
    compte = models.ForeignKey(CompteBanque, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=14, decimal_places=2)
    libelle = models.CharField(max_length=200)
    facture = models.ForeignKey(Facture, on_delete=models.SET_NULL, null=True, blank=True)
    date_mouvement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_mouvement} {self.montant} — {self.libelle}"
