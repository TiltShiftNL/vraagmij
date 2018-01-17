from django.db import models
from django.utils.translation import ugettext_lazy as _


class MyModel(models.Model):
    some_field = models.CharField(
        verbose_name=_('Some'),
        max_length=100,
    )
    image_field = models.ImageField(
        verbose_name=_('Afbeelding')
    )