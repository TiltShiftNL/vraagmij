from django.contrib import admin
from .models import *
from .forms import *
from adminsortable.admin import SortableAdmin
from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline
# from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.translation import ugettext_lazy as _


class VoorwaardeInline(SortableStackedInline):
    model = Voorwaarde
    extra = 1


class RegelingenTagsInline(SortableStackedInline):
    model = RegelingTag
    extra = 1


class ContactNaarRegelingInline(admin.TabularInline):
    model = ContactNaarRegeling
    extra = 1


class ContactNaarThemaInline(admin.TabularInline):
    model = ContactNaarThema
    extra = 1


class ContactNaarOrganisatieInline(admin.TabularInline):
    model = ContactNaarOrganisatie
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


@admin.register(Organisatie)
class OrganisatieAdmin(SortableAdmin):
    pass


# @admin.register(RegelingTag)
# class RegelingTagAdmin(SortableAdmin):
#     pass


@admin.register(Thema)
class ThemaAdmin(SortableAdmin):
    prepopulated_fields = {'slug': ('titel',), }
    inlines = [
        ContactNaarThemaInline,
    ]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    inlines = [
        ContactNaarOrganisatieInline,
        ContactNaarThemaInline,
    ]


@admin.register(EventItem)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'value', 'timestamp', 'url', ]
    list_filter = ['url', 'name', ]


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
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
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm


# admin.site.unregister(Group)
# @admin.register(Group)
# class CustomGroupAdmin(GroupAdmin):
#     pass

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     pass
