from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinical', '0001_initial'),
        ('users', '0005_user_en_pause_infirmier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('ADMIN', 'Administrateur'),
                    ('SECRETAIRE_GENERALE', 'Secrétaire générale'),
                    ('MEDECIN', 'Médecin'),
                    ('INFIRMIER', 'Infirmier'),
                    ('SECRETAIRE', 'Secrétaire'),
                    ('RECEPTIONNISTE', 'Réceptionniste'),
                    ('BIOLOGISTE', 'Biologiste'),
                    ('PATIENT', 'Patient'),
                ],
                default='PATIENT',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='docteur',
            name='services',
            field=models.ManyToManyField(
                blank=True,
                help_text='Services où le médecin exerce (pédiatrie, biologie, etc.)',
                related_name='medecins_affectes',
                to='clinical.service',
            ),
        ),
    ]
