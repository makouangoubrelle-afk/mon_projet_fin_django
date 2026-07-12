from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_otp_channel_sms'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='otp_channel',
            field=models.CharField(
                choices=[('EMAIL', 'Email'), ('SMS', 'SMS (téléphone)')],
                default='EMAIL',
                help_text='Canal pour recevoir le code de connexion OTP',
                max_length=10,
            ),
        ),
    ]
