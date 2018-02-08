from django.contrib import admin
from .models import *


@admin.register(Regeling)
class RegelingAdmin(admin.ModelAdmin):
    pass
    #raw_id_fields = ('voorwaarde_lijst',)

@admin.register(Voorwaarde)
class VoorwaardeAdmin(admin.ModelAdmin):
    pass


#admin.register(MyModel, MyModelAdmin)
#admin.site.register(MyModel, MyModelAdmin)