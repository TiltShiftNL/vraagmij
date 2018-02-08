from django.db import models
from django.utils.translation import ugettext_lazy as _
from sortedm2m.fields import SortedManyToManyField


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
    voorwaarde_lijst = SortedManyToManyField('Voorwaarde')

    def __str__(self):
        return '%s(%s)' % (self.titel, self.voorwaarde_lijst.all().count())

    class Meta:
        verbose_name = _('Regeling')
        verbose_name_plural = _('Regelingen')


class Voorwaarde(models.Model):
    titel = models.CharField(
        verbose_name=_('titel'),
        max_length=255,
    )


    def __str__(self):
        return self.titel

    class Meta:
        verbose_name = _('Voorwaarde')
        verbose_name_plural = _('Voorwaarden')
