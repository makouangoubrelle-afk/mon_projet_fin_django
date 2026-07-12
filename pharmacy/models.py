from django.db import models
from admission.models import Patient

class Medicament(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    code_barre = models.CharField(max_length=50, unique=True, null=True, blank=True)
    quantite_en_stock = models.IntegerField(default=0)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix de vente d'une boîte/unité")
    date_expiration = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom} (Stock: {self.quantite_en_stock})"

class PrescriptionPharmacie(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="achats_pharmacie")
    medicament = models.ForeignKey(Medicament, on_delete=models.PROTECT, related_name="ventes")
    quantite_delivree = models.IntegerField()
    frais_pharmacie_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    date_dispensation = models.DateTimeField(auto_now_add=True)
    est_paye = models.BooleanField(default=False)

    def save(self, *saved, **kwargs):
        # Calcul automatique du coût total de la ligne avant d'enregistrer
        self.frais_pharmacie_total = self.quantite_delivree * self.medicament.prix_unitaire
        super().save(*saved, **kwargs)

    def __str__(self):
        return f"{self.quantite_delivree}x {self.medicament.nom} pour {self.patient.nom}"