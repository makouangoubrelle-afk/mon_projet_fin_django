import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinical', '0004_casurgence_salleattente'),
        ('users', '0004_docteur'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='en_pause',
            field=models.BooleanField(default=False, help_text='Personnel en pause / indisponible'),
        ),
        migrations.CreateModel(
            name='Infirmier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telephone', models.CharField(max_length=20)),
                ('numero_ordre', models.CharField(blank=True, default='', max_length=30)),
                ('est_actif', models.BooleanField(default=True)),
                ('en_pause', models.BooleanField(default=False)),
                ('date_enregistrement', models.DateTimeField(auto_now_add=True)),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='infirmiers', to='clinical.service')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profil_infirmier', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Infirmier(ère)',
                'verbose_name_plural': 'Infirmiers(ères)',
                'ordering': ['nom', 'prenom'],
            },
        ),
    ]
