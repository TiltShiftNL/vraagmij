# Generated by Django 2.0.1 on 2018-02-15 15:21

from django.db import migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0017_auto_20180215_1414'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='regeling',
            options={'ordering': ('titel',), 'verbose_name': 'Regeling', 'verbose_name_plural': 'Regelingen'},
        ),
        migrations.AlterField(
            model_name='regeling',
            name='doelen',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='jeugdzorg.Doel'),
        ),
    ]