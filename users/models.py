from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    CHOIX_ROLES = [
        ('ADMIN', 'Administrateur'),
        ('SECRETAIRE_GENERALE', 'Secrétaire générale'),
        ('MEDECIN', 'Médecin'),
        ('INFIRMIER', 'Infirmier'),
        ('SECRETAIRE', 'Secrétaire'),
        ('RECEPTIONNISTE', 'Réceptionniste'),
        ('BIOLOGISTE', 'Biologiste / Laborantin'),
        ('PHARMACIEN', 'Pharmacien'),
        ('PATIENT', 'Patient'),
    ]
    role = models.CharField(max_length=20, choices=CHOIX_ROLES, default='PATIENT')
    telephone = models.CharField(max_length=20, blank=True, default='')
    service = models.ForeignKey(
        'clinical.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personnel',
    )
    en_pause = models.BooleanField(default=False, help_text='Personnel en pause / indisponible')
    OTP_CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS (téléphone)'),
    ]
    otp_channel = models.CharField(
        max_length=10,
        choices=OTP_CHANNEL_CHOICES,
        default='EMAIL',
        help_text='Canal pour recevoir le code de connexion OTP',
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class OtpCode(models.Model):
    """Code à usage unique renouvelé à chaque connexion par email."""
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    channel = models.CharField(max_length=10, default='EMAIL')  # EMAIL | SMS
    phone = models.CharField(max_length=30, blank=True, default='')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP {self.email} ({'utilisé' if self.is_used else 'actif'})"


class Docteur(models.Model):
    SPECIALITE_CHOICES = [
        ('Cardiologie', 'Cardiologie'),
        ('Neurologie', 'Neurologie'),
        ('Pédiatrie', 'Pédiatrie'),
        ('Gynécologie', 'Gynécologie'),
        ('Dermatologie', 'Dermatologie'),
        ('Orthopédie', 'Orthopédie'),
        ('Psychiatrie', 'Psychiatrie'),
        ('Ophtalmologie', 'Ophtalmologie'),
        ('Urgences', 'Urgences'),
        ('Médecine générale', 'Médecine générale'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profil_medecin',
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=50, choices=SPECIALITE_CHOICES, default='Médecine générale')
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField(blank=True, default='')
    numero_ordre = models.CharField(max_length=30, blank=True, default='', help_text="N° ordre des médecins")
    photo = models.URLField(blank=True, default='')
    est_actif = models.BooleanField(default=True)
    service = models.ForeignKey(
        'clinical.Service', on_delete=models.SET_NULL, null=True, blank=True, related_name='medecins',
    )
    services = models.ManyToManyField(
        'clinical.Service', blank=True, related_name='medecins_affectes',
        help_text='Services où le médecin exerce (pédiatrie, biologie, etc.)',
    )
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Médecin'
        verbose_name_plural = 'Médecins'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"Dr. {self.nom} {self.prenom} — {self.specialite}"


class Infirmier(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profil_infirmier',
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    numero_ordre = models.CharField(max_length=30, blank=True, default='')
    est_actif = models.BooleanField(default=True)
    en_pause = models.BooleanField(default=False)
    service = models.ForeignKey(
        'clinical.Service', on_delete=models.SET_NULL, null=True, blank=True, related_name='infirmiers',
    )
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Infirmier(ère)'
        verbose_name_plural = 'Infirmiers(ères)'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"
