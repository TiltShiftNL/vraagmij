from adminsortable.admin import SortableAdmin
from adminsortable.admin import SortableStackedInline
from django.contrib import admin
# from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .forms import *


class VoorwaardeInline(SortableStackedInline):
    model = Voorwaarde
    extra = 1


class RegelingenTagsInline(SortableStackedInline):
    model = RegelingTag
    extra = 1


class ProfielNaarOrganisatieInline(admin.TabularInline):
    model = ProfielNaarOrganisatie
    extra = 1


class ProfielNaarThemaInline(admin.TabularInline):
    model = ProfielNaarThema
    extra = 1


class ProfielNaarRegelingInline(admin.TabularInline):
    model = ProfielNaarRegeling
    extra = 1


class ProfielInline(admin.TabularInline):
    model = Profiel
    extra = 3


@admin.register(Regeling)
class RegelingAdmin(SortableAdmin):
    list_display = ['titel', 'bron_veranderd', 'datum_gecreeerd', 'datum_opgeslagen']

    inlines = [
        VoorwaardeInline,
    ]


@admin.register(Voorwaarde)
class VoorwaardeAdmin(SortableAdmin):
    pass


@admin.register(Organisatie)
class OrganisatieAdmin(SortableAdmin):
    pass


@admin.register(Gebied)
class GebiedAdmin(admin.ModelAdmin):
    list_display = ['naam', 'stadsdeel', ]
    list_filter = ['stadsdeel', ]
    prepopulated_fields = {'slug': ('naam',), }


@admin.register(Stadsdeel)
class StadsdeelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('naam',), }


@admin.register(Thema)
class ThemaAdmin(admin.ModelAdmin):
    list_display = ['titel', ]


@admin.register(EventItem)
class EventItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'value', 'timestamp', 'url', 'session_id', 'user']
    list_filter = ['url', 'name', 'session_id', 'user']


@admin.register(Profiel)
class ProfielAdmin(admin.ModelAdmin):
    list_display = ['gebruiker', 'voornaam', 'achternaam', 'email', 'gebruiker_email_verificatie', 'telefoonnummer', 'gebruik_email', 'gebruik_telefoonnummer', 'seconden_niet_gebruikt']
    list_filter = ['gebruiker_email_verificatie', ]
    inlines = [
        ProfielNaarRegelingInline,
        ProfielNaarThemaInline,
        ProfielNaarOrganisatieInline,
    ]


@admin.register(Instelling)
class InstellingAdmin(admin.ModelAdmin):
    list_display = ['site', 'app_naam', 'standaard_contact_naam', 'standaard_contact_email', ]
    save_on_top = True


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['email', 'is_active', 'is_staff', 'is_superuser', 'wijzig_profiel', 'date_saved']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('voornaam', 'tussenvoegsel', 'achternaam')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    def wijzig_profiel(self, obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label,  'profiel'),  args=[obj.profiel.id])
        return mark_safe("""<a id="edit_related" class="button related-widget-wrapper-link add-related" href="%s?_popup=1">Profiel</a>""" % url)

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    ordering = []




# admin.site.unregister(Group)
# @admin.register(Group)
# class CustomGroupAdmin(GroupAdmin):
#     pass

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     pass
