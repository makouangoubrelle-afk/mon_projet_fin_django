import uuid

from django.db import migrations, models

import admission.models


def fill_qr_codes(apps, schema_editor):
    Patient = apps.get_model('admission', 'Patient')
    for patient in Patient.objects.all():
        patient.qr_code = str(uuid.uuid4())
        patient.save(update_fields=['qr_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0005_clientprivilegie'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='qr_code',
            field=models.CharField(editable=False, max_length=36, null=True),
        ),
        migrations.RunPython(fill_qr_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='patient',
            name='qr_code',
            field=models.CharField(default=admission.models.generate_qr_code, editable=False, max_length=36, unique=True),
        ),
    ]
