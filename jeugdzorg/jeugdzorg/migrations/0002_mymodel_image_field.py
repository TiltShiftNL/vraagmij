# Generated by Django 2.0.1 on 2018-01-17 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mymodel',
            name='image_field',
            field=models.ImageField(default=0, upload_to='', verbose_name='Afbeelding'),
            preserve_default=False,
        ),
    ]
