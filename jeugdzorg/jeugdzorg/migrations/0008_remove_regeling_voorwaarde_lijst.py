# Generated by Django 2.0.1 on 2018-02-08 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0007_auto_20180208_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='regeling',
            name='voorwaarde_lijst',
        ),
    ]