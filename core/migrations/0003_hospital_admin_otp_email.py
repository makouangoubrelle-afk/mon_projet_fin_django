from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_hospital_ui_branding'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospitalsettings',
            name='admin_otp_email',
            field=models.EmailField(
                blank=True,
                default='',
                help_text="Email de l'administrateur principal pour la connexion OTP",
                max_length=254,
            ),
        ),
    ]
