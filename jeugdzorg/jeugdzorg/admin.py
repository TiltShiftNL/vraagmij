from django.contrib import admin
from .models import *
from adminsortable.admin import SortableAdmin
from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline


class VoorwaardeInline(SortableStackedInline):
    model = Voorwaarde
    extra = 1


class RegelingenTagsInline(SortableStackedInline):
    model = RegelingTag
    extra = 1


class ContactNaarRegelingInline(admin.TabularInline):
    model = ContactNaarRegeling
    extra = 1


@admin.register(Regeling)
class RegelingAdmin(SortableAdmin):
    list_display = ['titel', 'bron_veranderd']
    #raw_id_fields = ['contact', ]

    inlines = [
        VoorwaardeInline,
        ContactNaarRegelingInline,
    ]
    #filter_horizontal = ('contact',)  #


@admin.register(Voorwaarde)
class VoorwaardeAdmin(SortableAdmin):
    pass


@admin.register(RegelingTag)
class RegelingTagAdmin(SortableAdmin):
    pass


@admin.register(Doel)
class DoelAdmin(SortableAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass

