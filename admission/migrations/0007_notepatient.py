from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0006_patient_qr_code'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotePatient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenu', models.TextField()),
                ('est_important', models.BooleanField(default=False)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notes_redigees', to=settings.AUTH_USER_MODEL)),
                ('medecin', models.ForeignKey(blank=True, limit_choices_to={'role': 'MEDECIN'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notes_patients', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes_suivi', to='admission.patient')),
            ],
            options={
                'verbose_name': 'Note patient',
                'ordering': ['-date_creation'],
            },
        ),
    ]
