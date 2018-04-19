from django.core.exceptions import ValidationError
from croniter import croniter
from .models import *
from django.utils.safestring import mark_safe
from django.core.validators import EmailValidator


class CustomPasswordValidator(object):

    def __init__(self, min_length=1):
        self.min_length = min_length

    def validate(self, password, user=None):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        if not any(char.isdigit() for char in password):
            raise ValidationError('Het wachtwoord moet minstens één cijfer bevatten.')
        if not any(char.isupper() for char in password):
            raise ValidationError('Het wachtwoord moet minstens één hoofdletter bevatten.')
        if not any(char.islower() for char in password):
            raise ValidationError('Het wachtwoord moet minstens één kleine letter bevatten.')
        if not any(char in special_characters for char in password):
            raise ValidationError('Het wachtwoord moet minstens één speciaal karakter bevatten.')

    def get_help_text(self):
        return ""


def crontab_format_validator(value):
    base = timezone.now()
    try:
        croniter(value, base)
    except:
        raise ValidationError('Dit crontab format is niet correct', code='error_code')
    return True


def file_size(value):
    limit = 5 * 1024 * 1024
    if value and value.size > limit:
        raise ValidationError('De bestandsgrootte van de pasfoto is meer dan 5MB.', code='error_code')


def file_type(value):
    file_types = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
    ]
    if value.content_type not in file_types:
        raise ValidationError('Je mag voor de pasfoto alleen .jpg, .png en .gif bestanden gebruiken.', code='error_code')


def user_email_validation(value):
    instelling = None
    try:
        site = Site.objects.get_current()
        instelling = Instelling.objects.get(site=site)
    except:
        pass

    domeinen = list(set([dd for d in Organisatie.objects.all() for dd in d.email_domeinen_lijst()]))
    validator = EmailValidator()
    try:
        validator(value)
    except ValidationError:
        pass

    if value.rsplit('@', 1)[1] not in domeinen:
        raise ValidationError(
            mark_safe('Dit e-mailadres kan niet worden gebruikt. '
            'Het lijkt erop dat deze bijbehorende organisatie nog niet is aangemeld. '
            'Stuur een mail naar <a href="mailto:%s">%s</a>' % (
                instelling.standaard_contact_email,
                instelling.standaard_contact_naam,
            )),
            code='invalid'
        )

    return True