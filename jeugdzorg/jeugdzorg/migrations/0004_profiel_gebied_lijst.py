# Generated by Django 2.0.2 on 2018-03-10 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0003_auto_20180310_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='profiel',
            name='gebied_lijst',
            field=models.ManyToManyField(to='jeugdzorg.Gebied', verbose_name='Gebieden'),
        ),
    ]
