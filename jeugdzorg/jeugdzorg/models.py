from django.db import models
from adminsortable.models import SortableMixin
from adminsortable.fields import SortableForeignKey
from django.db.models import ManyToManyField
from django.db.models.fields.files import ImageFieldFile, ImageField
from django.forms import model_to_dict
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase
from sortedm2m.fields import SortedManyToManyField
from adminsortable.models import Sortable
from django.core.files.storage import default_storage
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save, pre_save
from .fields import EmailToLowerField
from django.conf import settings
from itertools import groupby
from django.contrib.sites.models import Site
from django.core.management import call_command
import json
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)

# fs = default_storage
# fs.container_name = 'jeugdzorg_protected'


class PrintableModel(models.Model):
    printable_fields = []
    printable_related_fields = []
    # def __repr__(self):
    #     return str(self.to_dict())

    def to_dict(self, **kwargs):
        opts = self._meta
        data = {}

        for f in opts.concrete_fields + opts.many_to_many:
            if f.value_from_object(self) and f.name in self.printable_fields:
                if isinstance(f, ManyToManyField):
                    if self.pk is None:
                        data[f.name] = []
                    else:
                        str_list = list([ff.__str__() for ff in f.value_from_object(self)])
                        data[f.name] = str_list

                elif isinstance(f, PhoneNumberField):
                    pass
                elif isinstance(f, ImageField):
                    pass
                    # print(f.value_from_object(self))
                    # print(dir(f.value_from_object(self)))
                    # if getattr(f.value_from_object(self), 'file'):
                    #     data[f.name] = f.value_from_object(self).file.path
                    # try:
                    # except ValueError as e:
                    #     pass
                else:
                    data[f.name] = f.value_from_object(self)
        for f in self.printable_related_fields:
            data['%s_set' % f] = list([ff.__str__() for ff in getattr(self, '%s_set' % f).all()])
        return data

    def to_json(self):
        return json.dumps(self.to_dict())

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    voornaam = models.CharField(_('voornaam'), max_length=100, blank=True)
    achternaam = models.CharField(_('achternaam'), max_length=150, blank=True)
    tussenvoegsel = models.CharField(
        verbose_name=_('Tussenvoegsel'),
        max_length=20,
        null=True,
        blank=True,
    )
    email = EmailToLowerField(unique=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    date_saved = models.DateTimeField(
        verbose_name=_('date saved'),
        auto_now=True,
        null=True,
        blank=True,
    )
    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return 'email: %s' % self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    class Meta:
        verbose_name = _('Gebruiker')
        verbose_name_plural = _("Gebruikers")


class Regeling(PrintableModel, models.Model):
    titel = models.CharField(
        verbose_name=('titel'),
        max_length=255,
    )
    samenvatting = models.TextField(
        verbose_name=_('Samenvatting'),
        null=True,
        blank=True,
    )
    bron = models.CharField(
        verbose_name=_('Bron'),
        max_length=255,
        null=True,
        blank=True,
    )
    startdatum = models.DateField(
        verbose_name=_('Start datum'),
        null=True,
        blank=True,
    )
    einddatum = models.DateField(
        verbose_name=_('Eind datum'),
        null=True,
        blank=True,
    )
    bron_url = models.URLField(
        verbose_name=_('Bron url'),
        null=True,
        blank=True,
    )
    bron_html_query = models.TextField(
        verbose_name=_('Bron html queryselector'),
        null=True,
        blank=True,
    )
    bron_veranderd = models.BooleanField(
        verbose_name=_('Bron veranderd'),
        default=False,
    )
    bron_resultaat = models.TextField(
        verbose_name=_('Bron resultaat'),
        null=True,
        blank=True,
    )
    aanvraag_url = models.URLField(
        verbose_name=_('Aaanvraag url'),
        null=True,
        blank=True,
    )
    tags = TaggableManager(
        through='TaggedRegeling',
        blank=True,
    )
    themas = SortedManyToManyField(
        to='Thema',
        blank=True,
    )
    datum_gecreeerd = models.DateTimeField(
        verbose_name=_('Datum gecreëerd'),
        auto_now_add=True,
        null=True,
        blank=True,
    )
    datum_opgeslagen = models.DateTimeField(
        verbose_name=_('Datum opgeslagen'),
        auto_now=True,
        null=True,
        blank=True,
    )

    printable_fields = [
        'id',
        'titel',
        'samenvatting',
        'themas',
    ]
    printable_related_fields = [
        'voorwaarde',
    ]

    objects = models.Manager()
    search = models.Manager()

    def voorwaarde_lijst(self):
        return Voorwaarde.objects.all()

    def profielen_zichtbaar(self):
        return self.regelingnaarprofiel.filter(profiel__zichtbaar=True)

    def first_letter(self):
        return self.titel and self.titel[0].upper() or ''

    def __str__(self):
        return '%s' % (self.titel)

    class Meta:
        verbose_name = _('Regeling')
        verbose_name_plural = _('Regelingen')
        ordering = ('titel', )


class Voorwaarde(SortableMixin):
    titel = models.CharField(
        verbose_name=_('titel'),
        max_length=255,
    )
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    datum_gecreeerd = models.DateTimeField(
        verbose_name=_('Datum gecreëerd'),
        auto_now_add=True,
        null=True,
        blank=True,
    )
    datum_opgeslagen = models.DateTimeField(
        verbose_name=_('Datum opgeslagen'),
        auto_now=True,
        null=True,
        blank=True,
    )

    regeling = SortableForeignKey(
        to=Regeling,
        verbose_name=_('Regeling'),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.titel

    class Meta:
        verbose_name = _('Voorwaarde')
        verbose_name_plural = _('Voorwaarden')
        ordering = ['order']


class RegelingTag(TagBase):
    omschrijving = models.TextField(
        verbose_name=_('Omschrijving'),
        null=True,
        blank=True,
    )


class TaggedRegeling(GenericTaggedItemBase):
    # TaggedWhatever can also extend TaggedItemBase or a combination of
    # both TaggedItemBase and GenericTaggedItemBase. GenericTaggedItemBase
    # allows using the same tag for different kinds of objects, in this
    # example Food and Drink.

    # Here is where you provide your custom Tag class.
    tag = models.ForeignKey(
        to=RegelingTag,
        related_name="%(app_label)s_%(class)s_items",
        on_delete=models.CASCADE,
    )


class Thema(PrintableModel, Sortable):
    titel = models.CharField(
        verbose_name=_('Titel'),
        max_length=255,
    )
    slug = models.SlugField(
        verbose_name=_('Url onderdeel'),
        null=True,
        blank=True,
    )
    omschrijving = models.TextField(
        verbose_name=_('Omschrijving'),
        null=True,
        blank=True,
    )
    objects = models.Manager()
    search = models.Manager()

    printable_fields = [
        'id',
        'titel',
        'omschrijving',
    ]

    def profielen_zichtbaar(self):
        return self.profiel_set.filter(zichtbaar=True)

    def first_letter(self):
        return self.titel and self.titel[0].upper() or ''

    def contacten(self):
        return self.contact.through.objects.filter(thema=self)

    def __str__(self):
        return self.titel

    class Meta(Sortable.Meta):
        verbose_name = _('Thema')
        verbose_name_plural = _("Thema's")


class Organisatie(models.Model):
    naam = models.CharField(
        verbose_name=_('Naam'),
        max_length=255,
    )
    email_domeinen = models.TextField(
        verbose_name=_('E-mailadres domeinen'),
        help_text=_('Voer meerdere domeinnamen in door ze met een komma te scheiden.'),
        null=True,
        blank=True,
    )

    def email_domeinen_lijst(self):
        if self.email_domeinen:
            return [d.strip() for d in self.email_domeinen.split(',')]
        return []

    def __str__(self):
        return self.naam

    def profielen_zichtbaar(self):
        return self.profiel_set.filter(zichtbaar=True)

    class Meta:
        verbose_name = _('Organisatie')
        verbose_name_plural = _("Organisaties")


class ProfielNaarOrganisatie(models.Model):
    profiel = models.ForeignKey(
        to='jeugdzorg.Profiel',
        verbose_name=_('Profiel'),
        related_name='profielnaarorganisatie',
        on_delete=models.CASCADE,
    )
    organisatie = models.ForeignKey(
        to='jeugdzorg.Organisatie',
        verbose_name=_('Organistie'),
        related_name='organisatienaarprofiel',
        on_delete=models.CASCADE,
    )
    volgorde = models.IntegerField(
        verbose_name=_('Volgorde'),
        default=0,
    )
    rol = models.CharField(
        verbose_name=_('Rol'),
        max_length=100,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Profiel naar organisatie')
        verbose_name_plural = _('Profielen naar organisaties')
        ordering = ('volgorde', )
        unique_together = ('profiel', 'organisatie', )


class ProfielNaarThema(models.Model):
    profiel = models.ForeignKey(
        to='jeugdzorg.Profiel',
        verbose_name=_('Profiel'),
        related_name='profielnaarthema',
        on_delete=models.CASCADE,
    )
    thema = models.ForeignKey(
        to='jeugdzorg.Thema',
        verbose_name=_('Thema'),
        related_name='themanaarprofiel',
        on_delete=models.CASCADE,
    )
    volgorde = models.IntegerField(
        verbose_name=_('Volgorde'),
        default=0,
    )
    rol = models.CharField(
        verbose_name=_('Rol'),
        max_length=100,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Profiel naar thema')
        verbose_name_plural = _("Profielen naar thema's")
        ordering = ('volgorde', )
        unique_together = ('profiel', 'thema', )


class ProfielNaarRegeling(models.Model):
    profiel = models.ForeignKey(
        to='jeugdzorg.Profiel',
        verbose_name=_('Profiel'),
        related_name='profielnaarregeling',
        on_delete=models.CASCADE,
    )
    regeling = models.ForeignKey(
        to='jeugdzorg.Regeling',
        verbose_name=_('Regeling'),
        related_name='regelingnaarprofiel',
        on_delete=models.CASCADE,
    )
    volgorde = models.IntegerField(
        verbose_name=_('Volgorde'),
        default=0,
    )
    rol = models.CharField(
        verbose_name=_('Rol'),
        max_length=100,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Profiel naar regeling')
        verbose_name_plural = _("Profielen naar regelingen")
        ordering = ('volgorde', )
        unique_together = ('profiel', 'regeling', )


class ProfielIsZichtbaarManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(zichtbaar=True)


class Profiel(PrintableModel, models.Model):
    seconden_niet_gebruikt = models.PositiveIntegerField(
        verbose_name=_('Seconden niet gebruikt'),
        null=True,
        blank=True,
        default=0,
    )
    zichtbaar = models.BooleanField(
        verbose_name=_('Zichtbaar'),
        help_text=_('Haal het vinkje, als je wil dat dit profiel onzichtbaar is voor andere.'),
        default=True,
    )
    gebruiker = models.OneToOneField(
        to='jeugdzorg.User',
        on_delete=models.SET_NULL,
        null=True,
    )
    email = models.EmailField(
        verbose_name=_('Primair e-mailadres'),
        blank=True,
        null=True,
    )
    telefoonnummer = PhoneNumberField(
        verbose_name=_('Primair telefoonnummer'),
        blank=True,
        null=True,
    )
    telefoonnummer_2 = PhoneNumberField(
        verbose_name=_('Secundair telefoonnummer'),
        blank=True,
        null=True,
    )
    gebruik_email = models.BooleanField(
        verbose_name=_('Gebruik e-mailadres'),
        default=True,
    )
    gebruik_telefoonnummer = models.BooleanField(
        verbose_name=_('Gebruik telefoonnummer'),
        default=True,
    )
    voornaam = models.CharField(
        verbose_name=_('Voornaam'),
        max_length=100,
        null=True,
        blank=True,
    )
    achternaam = models.CharField(
        verbose_name=_('Achternaam'),
        max_length=150,
        null=True,
        blank=True,
    )
    tussenvoegsel = models.CharField(
        verbose_name=_('Tussenvoegsel'),
        max_length=20,
        null=True,
        blank=True,
    )
    functie = models.CharField(
        verbose_name=_('Functie'),
        max_length=100,
        null=True,
        blank=True,
    )
    pasfoto = models.ImageField(
        verbose_name=_('Pasfoto'),
        upload_to='contact',
        null=True,
        blank=True,
    )
    vaardigheden = models.TextField(
        verbose_name=_('Vaardigheden'),
        null=True,
        blank=True,
    )
    hou_me_op_de_hoogte_mail = models.BooleanField(
        verbose_name=_('Hou me op de hoogte via e-mail'),
        default=False,
    )
    gebruiker_email_verificatie = models.CharField(
        verbose_name=_('Gebruiker email verificatie'),
        max_length=100,
        default='valid',
        null=True,
        blank=True,
    )
    gebruiker_email_verificatie_details = models.CharField(
        verbose_name=_('Gebruiker email verificatie details'),
        max_length=100,
        default='valid',
        null=True,
        blank=True,
    )
    organisatie_lijst = models.ManyToManyField(
        to='Organisatie',
        through='ProfielNaarOrganisatie',
        through_fields=('profiel', 'organisatie'),
    )
    thema_lijst = models.ManyToManyField(
        to='Thema',
        through='ProfielNaarThema',
        through_fields=('profiel', 'thema'),
    )
    regeling_lijst = models.ManyToManyField(
        to='Regeling',
        through='ProfielNaarRegeling',
        through_fields=('profiel', 'regeling'),
    )
    gebied_lijst = models.ManyToManyField(
        to='Gebied',
        verbose_name=_('Gebieden'),
        blank=True,
    )
    objects = models.Manager()
    is_zichtbaar = ProfielIsZichtbaarManager()
    search = ProfielIsZichtbaarManager()

    printable_fields = [
        'id',
        'seconden_niet_gebruikt',
        'email',
        'telefoonnummer',
        'telefoonnummer_2',
        'voornaam',
        'achternaam',
        'tussenvoegsel',
        'functie',
        'vaardigheden',
        'organisatie_lijst',
        'thema_lijst',
        'regeling_lijst',
        'gebied_lijst',
    ]

    @property
    def naam_volledig(self):
        if not self.voornaam and not self.achternaam:
            return ''
        if not self.achternaam:
            return '%s' % self.voornaam
        if not self.voornaam and self.tussenvoegsel:
            return '%s %s' % (self.tussenvoegsel, self.achternaam)
        if not self.tussenvoegsel:
            return '%s %s' % (self.voornaam, self.achternaam)
        return '%s %s %s' % (
            self.voornaam,
            self.tussenvoegsel,
            self.achternaam,
        )

    def alle_gebieden(self):
        out = {
            'gebied_lijst': [],
            'stadsdeel_lijst': [],
        }
        for k, gl in groupby(self.gebied_lijst.all().order_by('stadsdeel'), lambda x: x.stadsdeel):
            items = [g for g in gl]
            if Gebied.objects.filter(stadsdeel=k).count() == len(items):
                out['stadsdeel_lijst'].append(k)
            else:
                for gebied in items:
                    out['gebied_lijst'].append(gebied)
        return out

    def first_letter(self):
        return self.achternaam and self.achternaam[0].upper() or ''

    class Meta:
        verbose_name = _('Profiel')
        verbose_name_plural = _("Profielen")
        ordering = ('achternaam', )


class Stadsdeel(models.Model):
    naam = models.CharField(
        verbose_name=_('Naam'),
        max_length=100,
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
    )

    def __str__(self):
        return self.naam

    def first_letter(self):
        return self.naam and self.naam[0].upper() or ''

    class Meta:
        verbose_name = _('Stadsdeel')
        verbose_name_plural = _("Stadsdelen")
        ordering = ('naam', )


class Gebied(models.Model):
    naam = models.CharField(
        verbose_name=_('Naam'),
        max_length=100,
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
    )
    stadsdeel = models.ForeignKey(
        to='Stadsdeel',
        verbose_name=_('Stadsdeel'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.stadsdeel:
            return '%s - %s' % (
                self.naam,
                self.stadsdeel,
            )
        return self.naam

    def profielen_zichtbaar(self):
        return self.profiel_set.filter(zichtbaar=True)

    def first_letter(self):
        return self.naam and self.naam[0].upper() or ''

    class Meta:
        verbose_name = _('Gebied')
        verbose_name_plural = _("Gebieden")
        ordering = ('naam', )


class EventItem(models.Model):
    name = models.CharField(
        verbose_name=_('Naam'),
        max_length=255,
        null=True,
        blank=True,
    )
    value = models.CharField(
        verbose_name=_('Waarde'),
        max_length=255,
        null=True,
        blank=True,
    )
    url = models.CharField(
        verbose_name=_('Url'),
        max_length=255,
        null=True,
        blank=True,
    )
    timestamp = models.CharField(
        verbose_name=_('Timestamp'),
        max_length=255,
        null=True,
        blank=True,
    )
    session_id = models.CharField(
        verbose_name=_('Session id'),
        max_length=255,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('Gebruiker'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Gebruikers gedrag')
        verbose_name_plural = _("Gebruikers gedragingen")


class Instelling(models.Model):
    # __update_mail_frequentie = None
    # __gebruiker_email_verificatie_frequentie = None
    # __original_update_mail_frequentie = None

    site = models.OneToOneField(
        to=Site,
        verbose_name=_('Site'),
        on_delete=models.CASCADE,
    )
    app_naam = models.CharField(
        verbose_name=_('App naam'),
        default='VraagMij',
        max_length=30,
        null=True,
        blank=True,
    )
    standaard_contact_naam = models.CharField(
        verbose_name=_('Standaard contact naam'),
        max_length=100,
        null=True,
        blank=True,
    )
    standaard_contact_email = models.EmailField(
        verbose_name=_('Standaard contact e-mailadres'),
        null=True,
        blank=True,
    )
        # update_mail_ = models.PositiveIntegerField(
        #     verbose_name=_('Deactiveer limit'),
        #     help_text=_("Standaard is maandelijks. Crontab format 'MIN HOUR DOM MON DOW CMD'"),
        #     max_length=30,
        #     default='0 0 1 * *',
        # )
    send_update_mail_frequentie = models.CharField(
        verbose_name=_('Update mail frequentie'),
        help_text=_("Standaard is maandelijks. Crontab format 'MIN HOUR DOM MON DOW'"),
        max_length=30,
        default='0 0 1 * *',
    )
    update_mail_content = models.TextField(
        verbose_name=_('Update mail content'),
        null=True,
        blank=True,
    )
    update_mail_content_html = models.TextField(
        verbose_name=_('Update mail content html'),
        null=True,
        blank=True,
    )
    gebruiker_email_verificatie_frequentie = models.CharField(
        verbose_name=_('Gebruiker email verificatie frequentie'),
        help_text=_("Standaard is maandelijks. Crontab format 'MIN HOUR DOM MON DOW'"),
        max_length=30,
        default='0 0 1 * *',
    )
    update_regelingen_frequentie = models.CharField(
        verbose_name=_('Regelingen webpagina controlle frequentie'),
        help_text=_("Standaard is maandelijks. Crontab format 'MIN HOUR DOM MON DOW'"),
        max_length=30,
        default='0 0 1 * *',
    )
    check_user_activity_frequentie = models.CharField(
        verbose_name=_('Gebruikers activiteit synchronisatie frequentie'),
        help_text=_("Standaard is maandelijks. Crontab format 'MIN HOUR DOM MON DOW'"),
        max_length=30,
        default='0 0 1 * *',
    )

    @staticmethod
    def track_field_names():
        return (
            'send_update_mail_frequentie',
            'gebruiker_email_verificatie_frequentie',
            'update_regelingen_frequentie',
            'check_user_activity_frequentie',
        )

    class Meta:
        verbose_name = _('Instelling')
        verbose_name_plural = _("Instellingen")


class CronjobState(models.Model):
    naam_command = models.CharField(
        verbose_name='Naam',
        max_length=255,
    )
    datumtijd_command = models.DateTimeField(
        verbose_name='Datumtijd',
    )
    datumtijd_string = models.CharField(
        verbose_name='Datumtijd tekst',
        max_length=255,
    )
    log_command = models.TextField(
        verbose_name='Log',
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.naam_command

    class Meta:
        verbose_name = _('Cronjob status')
        verbose_name_plural = _("Cronjob statussen")


# def save_profile(sender, instance, **kwargs):
#     if kwargs.get('created') and not Profiel.objects.filter(gebruiker=instance):
#         p = Profiel(gebruiker=instance)
#         p.email = instance.email
#         p.voornaam = instance.first_name
#         p.achternaam = instance.last_name
#         p.save()


def save_instelling(sender, update_fields, instance, **kwargs):
    if hasattr(sender, 'track_field_names'):
        call_create_crontabs = [field_name for field_name in sender.track_field_names() if getattr(instance, '__%s' % field_name) != getattr(instance, '%s' % field_name)]
        if call_create_crontabs:
            call_command('create_crontabs')


def pre_save_instance(sender, instance, *args, **kwargs):
    if instance.id:
        if hasattr(sender, 'track_field_names'):
            for field_name in sender.track_field_names():
                setattr(instance, '__%s' % field_name, getattr(instance.__class__.objects.get(id=instance.id), field_name))


def rebuild_index_check(sender, update_fields, instance, **kwargs):
    call_command('rebuild_index')


# post_save.connect(save_profile, sender=User)
post_save.connect(save_instelling, sender=Instelling)
pre_save.connect(pre_save_instance, sender=Instelling)

# post_save.connect(rebuild_index_check, sender=Thema)
# post_save.connect(rebuild_index_check, sender=Regeling)
# post_save.connect(rebuild_index_check, sender=Profiel)

