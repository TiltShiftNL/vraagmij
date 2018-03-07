from django.db import models
from adminsortable.models import SortableMixin
from adminsortable.fields import SortableForeignKey
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
from django.db.models.signals import post_save

# fs = default_storage
# fs.container_name = 'jeugdzorg_protected'


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
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    email = models.EmailField(unique=True, null=True)
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


class Regeling(models.Model):
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
    contact = models.ManyToManyField(
        to='Contact',
        through='ContactNaarRegeling',
        through_fields=('regeling', 'contact'),
    )

    def contacten(self):
        return self.contact.through.objects.filter(regeling=self)

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


class Thema(Sortable):
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
    contact = models.ManyToManyField(
        to='Contact',
        through='ContactNaarThema',
        through_fields=('thema', 'contact'),
    )

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

    def __str__(self):
        return self.naam

    class Meta:
        verbose_name = _('Organisatie')
        verbose_name_plural = _("Organisaties")


class Contact(models.Model):
    voornaam = models.CharField(
        verbose_name=_('Voornaam'),
        max_length=100,
    )
    achternaam = models.CharField(
        verbose_name=_('Achternaam'),
        max_length=100,
    )
    email = models.EmailField(
        verbose_name=_('E-mailadres'),
    )
    telefoonnummer = models.CharField(
        verbose_name=_('Telefoonnummer'),
        max_length=20,
        null=True,
        blank=True,
    )
    photo = models.ImageField(
        verbose_name=_('Pasfoto'),
        upload_to='contact',
        null=True,
        blank=True,
    )
    organisatie = models.ManyToManyField(
        to='Organisatie',
        through='ContactNaarOrganisatie',
        through_fields=('contact', 'organisatie'),
    )
    
    def first_letter(self):
        return self.achternaam and self.achternaam[0].upper() or ''

    def __str__(self):
        return '%s %s' % (self.voornaam, self.achternaam)

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacten')


class ContactNaarOrganisatie(models.Model):
    contact = models.ForeignKey(
        to=Contact,
        verbose_name=_('Contact'),
        related_name='contactnaarorganisatie',
        on_delete=models.CASCADE,
    )
    organisatie = models.ForeignKey(
        to=Organisatie,
        verbose_name=_('Organistie'),
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
        verbose_name = _('Contact naar organisatie')
        verbose_name_plural = _('Contacten naar organisaties')
        ordering = ('volgorde', )
        unique_together = ('contact', 'organisatie', )


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


class ContactNaarRegeling(models.Model):
    contact = models.ForeignKey(
        to=Contact,
        verbose_name=_('Contact'),
        related_name='contactnaarregeling',
        on_delete=models.CASCADE,
    )
    regeling = models.ForeignKey(
        to=Regeling,
        verbose_name=_('Regeling'),
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
    #
    # def __str__(self):
    #     return '%s naar %s' % (self.contact, self.regeling)

    class Meta:
        verbose_name = _('Contact naar regeling')
        verbose_name_plural = _('Contacten naar regelingen')
        ordering = ('volgorde', )
        unique_together = ('contact', 'regeling', )


class ContactNaarThema(models.Model):
    contact = models.ForeignKey(
        to=Contact,
        verbose_name=_('Contact'),
        related_name='contactnaarthema',
        on_delete=models.CASCADE,
    )
    thema = models.ForeignKey(
        to=Thema,
        verbose_name=_('Thema'),
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
    #
    # def __str__(self):
    #     return '%s naar %s' % (self.contact, self.regeling)

    class Meta:
        verbose_name = _('Contact naar thema')
        verbose_name_plural = _("Contacten naar thema's")
        ordering = ('volgorde', )
        unique_together = ('contact', 'thema', )


class Profiel(models.Model):
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
        max_length=100,
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

    def first_letter(self):
        return self.achternaam and self.achternaam[0].upper() or ''

    class Meta:
        verbose_name = _('Profiel')
        verbose_name_plural = _("Profielen")
        ordering = ['achternaam', ]


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
        verbose_name=_('Event id'),
        max_length=255,
        null=True,
        blank=True,
    )
    # user = models.ForeignKey(
    #     to='jeugdzorg.User',
    #     verbose_name=_('Gebruiker'),
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    # )

    class Meta:
        verbose_name = _('Gebruikers gedrag')
        verbose_name_plural = _("Gebruikers gedragingen")


# from django.apps import apps
# from django.contrib.auth import get_user_model
# from django.core.signals import setting_changed
# from django.dispatch import receiver
#
#
# @receiver(setting_changed)
# def user_model_swapped(**kwargs):
#     print(kwargs)
#     if kwargs['setting'] == 'AUTH_USER_MODEL':
#         apps.clear_cache()
#         from django.contrib.admin.models import LogEntry
#         LogEntry.UserModel = get_user_model()


# def save_profile(sender, instance, **kwargs):
#     if kwargs.get('created') and not Profiel.objects.filter(gebruiker=instance):
#         p = Profiel(gebruiker=instance)
#         p.email = instance.email
#         p.voornaam = instance.first_name
#         p.achternaam = instance.last_name
#         p.save()
#
# post_save.connect(save_profile, sender=User)