from django.contrib import admin
from .models import *
from adminsortable.admin import SortableAdmin
from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline



class VoorwaardeInline(SortableStackedInline):
    model = Voorwaarde
    extra = 1


@admin.register(Regeling)
class RegelingAdmin(SortableAdmin):
    inlines = [VoorwaardeInline]


@admin.register(Voorwaarde)
class VoorwaardeAdmin(SortableAdmin):
    pass
