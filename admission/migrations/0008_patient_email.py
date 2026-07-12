from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0007_notepatient'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='email',
            field=models.EmailField(blank=True, help_text='Email de connexion portail patient', max_length=254, null=True, unique=True),
        ),
    ]
