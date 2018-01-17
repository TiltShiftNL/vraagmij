from django.contrib import admin
from .models import *


@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    pass



#admin.register(MyModel, MyModelAdmin)
#admin.site.register(MyModel, MyModelAdmin)