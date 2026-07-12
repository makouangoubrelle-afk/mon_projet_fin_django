import uuid
from django.db import models


def generate_qr_code():
    return str(uuid.uuid4())

class Assurance(models.Model):
    nom = models.StringField(max_length=100) if False else models.CharField(max_length=100, unique=True)
    code_assurance = models.CharField(max_length=20, unique=True)
    taux_couverture = models.IntegerField(help_text="Pourcentage pris en charge par l'assurance (ex: 80 pour 80%)")
    adresse = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.taux_couverture}%)"

class Abonne(models.Model):
    nom_entreprise = models.CharField(max_length=100, unique=True)
    matricule_entreprise = models.CharField(max_length=50, unique=True)
    date_debut_contrat = models.DateField()
    date_fin_contrat = models.DateField()
    est_actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom_entreprise

GROUPE_SANGUIN_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]


class Patient(models.Model):
    GENRE_CHOICES = [
        ("M", "Masculin"),
        ("F", "Féminin"),
    ]
    
    # Informations de la Réception
    sgl_id = models.CharField(max_length=30, unique=True, help_text="Identifiant unique du patient à l'hôpital")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, null=True, blank=True, unique=True, help_text="Email de connexion portail patient")
    adresse = models.TextField(null=True, blank=True)
    numero_identite = models.CharField(max_length=30, null=True, blank=True, help_text="N° carte d'identité nationale")
    situation_familiale = models.CharField(max_length=20, null=True, blank=True)
    nombre_enfants = models.IntegerField(default=0)
    profession = models.CharField(max_length=100, null=True, blank=True)
    poids_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    taille_m = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_SANGUIN_CHOICES, null=True, blank=True)
    informations_medicales = models.TextField(
        null=True, blank=True,
        help_text="Allergies, antécédents, maladies chroniques, etc.",
    )
    allergies = models.TextField(null=True, blank=True, help_text="Allergies connues")
    antecedents_medicaux = models.TextField(null=True, blank=True, help_text="Antécédents médicaux détaillés")
    contact_urgence_nom = models.CharField(max_length=150, null=True, blank=True)
    contact_urgence_telephone = models.CharField(max_length=20, null=True, blank=True)
    contact_urgence_lien = models.CharField(max_length=80, null=True, blank=True, help_text="Parent, conjoint, ami…")
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    qr_code = models.CharField(max_length=36, unique=True, default=generate_qr_code, editable=False)

    # Prise en charge financière (Abonnés & Assurances)
    assurance = models.ForeignKey(Assurance, on_delete=models.SET_NULL, null=True, blank=True, related_name="patients")
    numero_assure = models.CharField(max_length=50, null=True, blank=True, help_text="Numéro de carte d'assurance")
    abonne = models.ForeignKey(Abonne, on_delete=models.SET_NULL, null=True, blank=True, related_name="employes_patients")
    user = models.OneToOneField(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dossier_patient',
    )

    def __str__(self):
        return f"{self.nom.upper()} {self.prenom} ({self.sgl_id})"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        years = today.year - self.date_naissance.year
        if (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day):
            years -= 1
        return max(years, 0)


class RendezVous(models.Model):
    STATUT_CHOICES = [
        ('PLANIFIE', 'Planifié'),
        ('CONFIRME', 'Confirmé'),
        ('ANNULE', 'Annulé'),
        ('TERMINE', 'Terminé'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rendez_vous')
    medecin = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='rendez_vous',
    )
    service = models.ForeignKey(
        'clinical.Service', on_delete=models.SET_NULL, null=True, blank=True, related_name='rendez_vous',
    )
    date_rdv = models.DateTimeField()
    motif = models.TextField()
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='PLANIFIE')
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date_rdv']
        verbose_name = 'Rendez-vous'
        verbose_name_plural = 'Rendez-vous'

    def __str__(self):
        return f"RDV {self.patient.sgl_id} — {self.date_rdv.strftime('%d/%m/%Y %H:%M')}"


class ClientPrivilegie(models.Model):
    TYPE_CARTE_CHOICES = [
        ('VIP', 'Carte VIP'),
        ('OR', 'Carte Or'),
        ('PREMIUM', 'Carte Premium'),
        ('FAMILLE', 'Carte Famille'),
    ]
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='privilege')
    numero_carte = models.CharField(max_length=30, unique=True)
    type_carte = models.CharField(max_length=15, choices=TYPE_CARTE_CHOICES, default='VIP')
    taux_reduction = models.IntegerField(default=10, help_text="Pourcentage de réduction (ex: 15 pour 15%)")
    date_expiration = models.DateField(null=True, blank=True)
    est_actif = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Client privilégié'
        verbose_name_plural = 'Clients privilégiés'

    def __str__(self):
        return f"{self.numero_carte} — {self.patient.nom} (-{self.taux_reduction}%)"


class NotePatient(models.Model):
    """Notes secrétariat / suivi patient pour le médecin."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='notes_suivi')
    auteur = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, related_name='notes_redigees',
    )
    medecin = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notes_patients', limit_choices_to={'role': 'MEDECIN'},
    )
    contenu = models.TextField()
    est_important = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Note patient'

    def __str__(self):
        return f"Note — {self.patient.sgl_id} ({self.date_creation.strftime('%d/%m/%Y')})"


class PatientChatMessage(models.Model):
    """Messagerie patient ↔ équipe médicale (support global par dossier)."""
    TYPE_CHOICES = [
        ('CHAT', 'Message'),
        ('RDV_DEMANDE', 'Demande de rendez-vous'),
        ('RDV_CONFIRME', 'Confirmation rendez-vous'),
        ('SYSTEM', 'Système'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='messages_chat')
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=150)
    sender_role = models.CharField(max_length=30, default='PATIENT')
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='CHAT')
    contenu = models.TextField()
    rendez_vous = models.ForeignKey(
        RendezVous, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages_chat',
    )
    metadata = models.JSONField(default=dict, blank=True)
    lu_par_patient = models.BooleanField(default=False)
    lu_par_equipe = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Message chat patient'
        verbose_name_plural = 'Messages chat patients'

    def __str__(self):
        return f"Chat {self.patient.sgl_id} — {self.sender_name} ({self.message_type})"