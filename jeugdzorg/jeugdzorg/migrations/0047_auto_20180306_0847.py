# Generated by Django 2.0.2 on 2018-03-06 08:47

from django.db import migrations
from django.db import migrations, transaction


class Migration(migrations.Migration):

    @transaction.atomic
    def create_unique_email(apps, schema_editor):
        User = apps.get_model("auth", "User")

        dummy_email_counter = 1
        current_email_counter = 1
        for user in User.objects.all():

            if user.email:
                address = user.email.split('@')[0]
                host = user.email.split('@')[1]
                current_email = user.email
                while User.objects.filter(email=current_email).count() > 1:
                    current_email = '%s%s@%s' % (
                        address,
                        current_email_counter,
                        host
                    )
                    current_email_counter += 1
                user.email = current_email
                user.save()
            else:
                dummy_email = 'email%s@host.com' % dummy_email_counter
                user.email = dummy_email
                dummy_email_counter += 1
                user.save()


    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('jeugdzorg', '0046_auto_20180302_1301'),
    ]

    operations = [
        migrations.RunPython(create_unique_email, migrations.RunPython.noop),
    ]
