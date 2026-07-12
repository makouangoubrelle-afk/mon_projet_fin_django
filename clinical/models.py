from django.conf import settings
from django.db import models
from admission.models import Patient


class Service(models.Model):
    """Service hospitalier avec secrétaire attitrée."""
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    batiment = models.CharField(max_length=50, default='Bâtiment A')
    etage = models.CharField(max_length=10, default='RDC')
    telephone = models.CharField(max_length=20, blank=True, default='')
    en_pause = models.BooleanField(default=False, help_text='Service en pause / fermé temporairement')
    secretaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services_geres',
        limit_choices_to={'role': 'SECRETAIRE'},
    )

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return f"{self.nom} ({self.batiment}, {self.etage})"


class Chambre(models.Model):
    TYPE_CHOICES = [
        ('STANDARD', 'Standard'),
        ('VIP', 'VIP'),
        ('REANIMATION', 'Réanimation'),
    ]
    STATUT_CHOICES = [
        ('LIBRE', 'Libre'),
        ('OCCUPEE', 'Occupée'),
        ('NETTOYAGE', 'En nettoyage'),
        ('MAINTENANCE', 'En maintenance'),
    ]
    numero = models.CharField(max_length=10, unique=True)
    type_chambre = models.CharField(max_length=20, choices=TYPE_CHOICES, default='STANDARD')
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='LIBRE')
    prix_journalier = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix par jour d'hospitalisation")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='chambres')
    batiment = models.CharField(max_length=50, default='Bâtiment A')
    etage = models.CharField(max_length=10, default='1')

    def __str__(self):
        return f"Chambre {self.numero} ({self.get_type_chambre_display()}) — {self.get_statut_display()}"

    def sync_statut_depuis_lits(self):
        """Met à jour le statut selon l'occupation des lits."""
        lits = list(self.lits.all())
        if not lits:
            return
        occupes = sum(1 for l in lits if l.est_occupe)
        if occupes > 0:
            self.statut = 'OCCUPEE'
        elif self.statut == 'OCCUPEE':
            self.statut = 'NETTOYAGE'
        self.save(update_fields=['statut'])


class Lit(models.Model):
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE, related_name="lits")
    code_lit = models.CharField(max_length=10)
    est_occupe = models.BooleanField(default=False)

    class Meta:
        unique_together = ('chambre', 'code_lit')

    def __str__(self):
        statut = "Occupé" if self.est_occupe else "Libre"
        return f"{self.chambre} - Lit {self.code_lit} ({statut})"


class Admission(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="hospitalisations")
    lit = models.ForeignKey(Lit, on_delete=models.SET_NULL, null=True, related_name="occupations")
    date_entree = models.DateTimeField(auto_now_add=True)
    date_sortie = models.DateTimeField(null=True, blank=True)
    motif_hospitalisation = models.TextField()
    est_cloture = models.BooleanField(default=False)
    frais_hebergement_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Hospitalisation de {self.patient.nom} (Entrée: {self.date_entree.strftime('%d/%m/%Y')})"


class LocalisationPatient(models.Model):
    """Suivi en temps réel de la position du patient dans l'hôpital."""
    STATUT_CHOICES = [
        ('ENREGISTRE', 'Enregistré à l\'accueil'),
        ('EN_ATTENTE', 'En salle d\'attente'),
        ('EN_CONSULTATION', 'En consultation'),
        ('EXAMEN', 'En examen'),
        ('HOSPITALISE', 'Hospitalisé'),
        ('SORTI', 'Sorti'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='localisations')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_presents')
    batiment = models.CharField(max_length=50, default='Bâtiment A')
    etage = models.CharField(max_length=10, default='RDC')
    salle = models.CharField(max_length=80, default='Accueil')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ENREGISTRE')
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_mise_a_jour']
        verbose_name = 'Localisation patient'

    def __str__(self):
        return f"{self.patient.sgl_id} → {self.batiment} / {self.salle}"


class BanqueSang(models.Model):
    """Stock de poches de sang par groupe sanguin."""
    GROUPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    STATUT_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('RESERVE', 'Réservé'),
        ('CRITIQUE', 'Stock critique'),
        ('EXPIRE', 'Expiré'),
    ]
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_CHOICES)
    numero_poche = models.CharField(max_length=30, unique=True)
    volume_ml = models.IntegerField(default=450)
    date_collecte = models.DateField()
    date_expiration = models.DateField()
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='DISPONIBLE')
    donneur_id = models.CharField(max_length=30, blank=True, default='')

    class Meta:
        verbose_name = 'Poche de sang'
        verbose_name_plural = 'Banque de sang'

    def __str__(self):
        return f"{self.groupe_sanguin} — {self.numero_poche} ({self.statut})"


class SalleAttente(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EN_CONSULTATION', 'En consultation'),
        ('TERMINE', 'Terminé'),
    ]
    PRIORITE_CHOICES = [
        ('NORMAL', 'Normal'),
        ('URGENT', 'Urgent'),
    ]
    TYPE_FILE_CHOICES = [
        ('STANDARD', 'Salle standard'),
        ('PRIVILEGE', 'Salle VIP privilèges'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='passages_attente')
    motif = models.TextField(blank=True, default='')
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='NORMAL')
    type_file = models.CharField(
        max_length=15, choices=TYPE_FILE_CHOICES, default='STANDARD',
        help_text='File standard ou salon réservé aux clients privilégiés',
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_arrivee = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_arrivee']
        verbose_name = "Salle d'attente"

    def __str__(self):
        return f"{self.patient.sgl_id} — {self.get_statut_display()}"


class CasUrgence(models.Model):
    SITUATION_CHOICES = [
        ('NORMAL', 'Normal'),
        ('IMPORTANT', 'Important'),
        ('CRITIQUE', 'Critique'),
    ]
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('STABLE', 'Stable'),
        ('SORTI', 'Sorti'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='cas_urgence')
    diagnostic = models.CharField(max_length=200)
    situation = models.CharField(max_length=15, choices=SITUATION_CHOICES, default='NORMAL')
    notes = models.TextField(blank=True, default='')
    traitement = models.TextField(blank=True, default='')
    examen_biologique = models.TextField(blank=True, default='')
    examen_radiologique = models.TextField(blank=True, default='')
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='EN_COURS')
    date_admission = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_admission']
        verbose_name = "Cas urgence"

    def __str__(self):
        return f"Urgence {self.patient.sgl_id} — {self.diagnostic}"
