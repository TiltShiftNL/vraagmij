# Generated by Django 2.0.1 on 2018-02-15 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeugdzorg', '0014_auto_20180215_1243'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='doel',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='doel',
            name='order',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
        ),
    ]