# Generated by Django 2.0.1 on 2018-02-28 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0028_contact_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='photo',
            field=models.ImageField(blank=True, null=True, storage='jeugdzorg', upload_to='contact', verbose_name='Pas foto'),
        ),
    ]