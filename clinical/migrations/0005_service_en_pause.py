from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinical', '0004_casurgence_salleattente'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='en_pause',
            field=models.BooleanField(default=False, help_text='Service en pause / fermé temporairement'),
        ),
    ]
