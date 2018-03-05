"""jeugdzorg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', ThemaList.as_view(), name='homepage'),
    path('regelingen/', RegelingList.as_view(), name='regelingen'),
    path('regeling-maken/', RegelingCreate.as_view(), name='create_regeling'),
    path('regeling/<int:pk>/bewerken', RegelingUpdate.as_view(), name='update_regeling'),
    path('regeling/<int:pk>/verwijderen', RegelingDelete.as_view(), name='verwijder_regeling'),
    path('regeling/<int:pk>/', RegelingDetail.as_view(), name='detail_regeling'),
    path('themas/', ThemaList.as_view(), name='themas'),
    path('thema/<slug:slug>/', ThemaDetail.as_view(), name='detail_thema'),
    path('contacten/', ContactList.as_view(), name='contacten'),
    path('contact/<int:pk>/', ContactDetail.as_view(), name='detail_contact'),
    path('contact/<int:pk>/bewerken', ContactUpdate.as_view(), name='update_contact'),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    
    path('event/add', EventView.as_view(), name='add_event'),

    path('admin/', admin.site.urls),
    path('admin/dumpjeugdzorg/', dump_jeugdzorg, name='dumpjeugdzorg'),
    path('admin/loadjeugdzorg/', load_jeugdzorg, name='loadjeugdzorg'),
    path('admin/logs/', ConfigView.as_view(), name='logs'),
]

urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)