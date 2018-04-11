# Generated by Django 2.0.2 on 2018-04-11 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0031_instelling_create_crontabs_frequentie'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pagina',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actief', models.BooleanField(default=False, verbose_name='Actief')),
                ('titel', models.CharField(max_length=50, verbose_name='Titel')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('inhoud', models.TextField(blank=True, help_text='Tekstopmaak kan verkregen worden door de Textile syntax te gebruiken. Zie: https://txstyle.org/', null=True, verbose_name='Inhoud')),
                ('order', models.PositiveIntegerField(db_index=True, default=0, editable=False)),
            ],
            options={
                'verbose_name': 'Pagina',
                'verbose_name_plural': "Pagina's",
                'ordering': ['order'],
            },
        ),
    ]