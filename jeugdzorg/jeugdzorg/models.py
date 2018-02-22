from django.db import models
from django.utils.translation import ugettext_lazy as _
from adminsortable.models import SortableMixin
from adminsortable.fields import SortableForeignKey
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase
from sortedm2m.fields import SortedManyToManyField
from adminsortable.models import Sortable



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
    tags = TaggableManager(
        through='TaggedRegeling',
        blank=True,
    )
    doelen = SortedManyToManyField(
        to='Doel',
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
        return self.titel and self.titel[0] or ''

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


class Doel(Sortable):
    titel = models.CharField(
        verbose_name=_('Titel'),
        max_length=255,
    )
    omschrijving = models.TextField(
        verbose_name=_('Omschrijving'),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.titel

    class Meta(Sortable.Meta):
        verbose_name = _('Doel')
        verbose_name_plural = _('Doelen')


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

    def __str__(self):
        return '%s %s' % (self.voornaam, self.achternaam)

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacten')


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