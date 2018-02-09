# Generated by Django 2.0.1 on 2018-02-08 13:55

import adminsortable.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0006_regeling_voorwaarde_lijst'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regeling',
            name='voorwaarde_lijst',
            field=adminsortable.fields.SortableForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jeugdzorg.Voorwaarde', verbose_name='Voorwaarden'),
        ),
    ]
