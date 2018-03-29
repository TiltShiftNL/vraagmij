# Generated by Django 2.0.2 on 2018-03-27 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0020_profiel_gebruiker_email_verificatie_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='instelling',
            name='check_user_activity_frequentie',
            field=models.CharField(default='0 0 1 * *', help_text="Standaard is maandelijks. Crontab format 'MIN HOUR DOM MON DOW'", max_length=30, verbose_name='Gebruikers activiteit synchronisatie frequentie'),
        ),
        migrations.AddField(
            model_name='instelling',
            name='update_regelingen_frequentie',
            field=models.CharField(default='0 0 1 * *', help_text="Standaard is maandelijks. Crontab format 'MIN HOUR DOM MON DOW'", max_length=30, verbose_name='Regelingen webpagina controlle frequentie'),
        ),
    ]