import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0006_patient_qr_code'),
        ('clinical', '0003_chambre_statut'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalleAttente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motif', models.TextField(blank=True, default='')),
                ('priorite', models.CharField(choices=[('NORMAL', 'Normal'), ('URGENT', 'Urgent')], default='NORMAL', max_length=10)),
                ('statut', models.CharField(choices=[('EN_ATTENTE', 'En attente'), ('EN_CONSULTATION', 'En consultation'), ('TERMINE', 'Terminé')], default='EN_ATTENTE', max_length=20)),
                ('date_arrivee', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passages_attente', to='admission.patient')),
            ],
            options={
                'verbose_name': "Salle d'attente",
                'ordering': ['-date_arrivee'],
            },
        ),
        migrations.CreateModel(
            name='CasUrgence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diagnostic', models.CharField(max_length=200)),
                ('situation', models.CharField(choices=[('NORMAL', 'Normal'), ('IMPORTANT', 'Important'), ('CRITIQUE', 'Critique')], default='NORMAL', max_length=15)),
                ('notes', models.TextField(blank=True, default='')),
                ('traitement', models.TextField(blank=True, default='')),
                ('examen_biologique', models.TextField(blank=True, default='')),
                ('examen_radiologique', models.TextField(blank=True, default='')),
                ('statut', models.CharField(choices=[('EN_COURS', 'En cours'), ('STABLE', 'Stable'), ('SORTI', 'Sorti')], default='EN_COURS', max_length=15)),
                ('date_admission', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cas_urgence', to='admission.patient')),
            ],
            options={
                'verbose_name': 'Cas urgence',
                'ordering': ['-date_admission'],
            },
        ),
    ]
