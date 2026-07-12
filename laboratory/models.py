from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class Analyse(models.Model):
    STATUT_CHOICES = [
        ("COMMANDE", "Commande"),
        ("PRELEVEMENT", "Prelevement"),
        ("SAISIE", "Saisie"),
        ("VALIDE", "Valide"),
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    patient_dossier = models.ForeignKey(
        'admission.Patient',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='analyses',
    )
    examen_nom = models.CharField(max_length=100)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="COMMANDE")
    resultat = models.TextField(null=True, blank=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="analyses_validees"
    )
    est_immuable = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk:
            original = Analyse.objects.get(pk=self.pk)
            if original.est_immuable:
                raise ValidationError("Ce resultat est valide et ne peut plus etre modifie.")
        
        if self.statut == "VALIDE":
            self.est_immuable = True
            if not self.date_validation:
                self.date_validation = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.examen_nom} - {self.patient.username} ({self.statut})"