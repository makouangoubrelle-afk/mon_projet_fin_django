from django.db import models
from django.conf import settings
from admission.models import Patient

class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="consultations")
    medecin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="consultations_effectuees")
    
    # 1. Signes vitaux / Constantes (Infirmerie)
    tension_arterielle = models.CharField(max_length=20, null=True, blank=True, help_text="Ex: 12/8")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="En °C")
    poids = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="En kg")
    pouls = models.IntegerField(null=True, blank=True, help_text="Battements par minute")
    
    # 2. Informations Médicales (Médecin)
    motif_consultation = models.TextField()
    diagnostic = models.TextField(null=True, blank=True)
    notes_medicales = models.TextField(null=True, blank=True)
    
    # Tarification de base de la consultation (pour la facturation globale)
    frais_consultation = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00, help_text="Coût brut de l'acte médical")
    
    date_consultation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation de {self.patient.nom} par Dr. {self.medecin.username if self.medecin else 'Inconnu'}"


class Ordonnance(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ordonnances')
    consultation = models.ForeignKey(
        Consultation, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordonnances',
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ordonnances_redigees',
    )
    medicaments = models.TextField(help_text="Liste des médicaments prescrits et posologie")
    instructions = models.TextField(null=True, blank=True)
    date_ordonnance = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_ordonnance']

    def __str__(self):
        return f"Ordonnance — {self.patient.nom} ({self.date_ordonnance.strftime('%d/%m/%Y')})"