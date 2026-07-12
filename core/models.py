from django.db import models
from django.conf import settings


class HospitalSettings(models.Model):
    """Configuration globale de l'établissement (singleton)."""
    nom_hopital = models.CharField(max_length=200, default='SGHL — Hôpital Général')
    adresse = models.TextField(default='Pointe-Noire, Congo-Brazzaville')
    telephone = models.CharField(max_length=30, default='+242 06 000 00 00')
    email = models.EmailField(default='contact@sghl.com')
    site_web = models.URLField(blank=True, default='')
    logo_url = models.URLField(blank=True, default='')
    devise = models.CharField(max_length=10, default='CDF')
    fuseau_horaire = models.CharField(max_length=50, default='Africa/Brazzaville')
    horaires_ouverture = models.CharField(max_length=200, default='Lun–Dim 24h/24')
    directeur = models.CharField(max_length=150, blank=True, default='')
    siret = models.CharField(max_length=50, blank=True, default='')
    # Personnalisation interface (modifiable par l'administrateur)
    nom_application = models.CharField(max_length=80, default='SGHL')
    slogan_application = models.CharField(
        max_length=200,
        default='Système de Gestion Hospitalière et de Laboratoire',
    )
    icone_application = models.CharField(max_length=10, default='🏥')
    theme_ui = models.CharField(max_length=30, default='teal')
    config_style = models.JSONField(default=dict, blank=True)
    admin_otp_email = models.EmailField(
        blank=True,
        default='',
        help_text='Email de l\'administrateur principal pour la connexion OTP',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres de l'hôpital"
        verbose_name_plural = "Paramètres de l'hôpital"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.nom_hopital


class LoginHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_history',
    )
    email = models.EmailField(db_index=True)
    role = models.CharField(max_length=30, blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default='')
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Historique de connexion'
        verbose_name_plural = 'Historiques de connexion'


class ActivityLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
    )
    email = models.EmailField(db_index=True, blank=True, default='')
    role = models.CharField(max_length=30, blank=True, default='')
    action = models.CharField(max_length=100)
    module = models.CharField(max_length=80, blank=True, default='')
    detail = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journaux d'activité"


class Notification(models.Model):
    LEVEL_CHOICES = [
        ('INFO', 'Information'),
        ('SUCCESS', 'Succès'),
        ('WARNING', 'Avertissement'),
        ('DANGER', 'Urgent'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text='Null = notification globale (tous les utilisateurs)',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='INFO')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=300, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
