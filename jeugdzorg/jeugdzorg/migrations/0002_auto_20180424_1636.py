# Generated by Django 2.0.2 on 2018-04-24 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiel',
            name='gebruiker_email_verificatie_details',
            field=models.TextField(blank=True, default='valid', null=True, verbose_name='Gebruiker email verificatie details'),
        ),
    ]
