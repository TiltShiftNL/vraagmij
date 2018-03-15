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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import *
from .forms import *
from django.urls import re_path
from django.views.static import serve
from rest_framework import routers
from .api import RegelingViewSet

router = routers.DefaultRouter()
router.register(r'regelingen', RegelingViewSet)

urlpatterns = [
    # path('', CheckUserModel.as_view(), name='test'),
    # path('', ThemaList.as_view(), name='homepage'),
    path('', RegelingList.as_view(), name='homepage'),
    path('regelingen/', RegelingList.as_view(), name='regelingen'),
    path('regeling-maken/', RegelingCreate.as_view(), name='create_regeling'),
    path('regeling/<int:pk>/bewerken', RegelingUpdate.as_view(), name='update_regeling'),
    path('regeling/<int:pk>/verwijderen', RegelingDelete.as_view(), name='verwijder_regeling'),
    path('regeling/<int:pk>/', RegelingDetail.as_view(), name='detail_regeling'),
    path('themas/', ThemaList.as_view(), name='themas'),
    path('thema/<slug:slug>/', ThemaDetail.as_view(), name='detail_thema'),
    path('thema/<slug:slug>/regeling/<int:pk>/', RegelingDetail.as_view(), {'sub_view': 'themas'}, name='detail_regeling'),
    path('contacten/', ProfielList.as_view(), name='contacten'),
    path('contact/<int:pk>/', ProfielDetail.as_view(), name='detail_contact'),
    path('profiel/bewerken', ProfielUpdateView.as_view(), name='update_profiel'),

    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),

    path('event/add', EventView.as_view(), name='add_event'),

    path('admin/', admin.site.urls),
    path('admin/dumpjeugdzorg/', dump_jeugdzorg, name='dumpjeugdzorg'),
    path('admin/loadjeugdzorg/', load_jeugdzorg, name='loadjeugdzorg'),
    path('admin/logs/', ConfigView.as_view(), name='logs'),

    url('^', include('django.contrib.auth.urls')),


    url(r'^herstel-wachtwoord/$',
        password_reset_new_user,
        {'flow': 'default', },
        name='herstel_wachtwoord'
    ),
    url(r'^wachtwoord-instellen/$',
        password_reset_new_user,
        {'flow': 'new', },
        name='wachtwoord_instellen'
        ),
    url(r'^herstel-wachtwoord/verstuurd/$',
        auth_views.password_reset_done,
        name='herstel_wachtwoord_klaar'
        ),
    url(r'^wachtwoord-instellen/verstuurd/$',
        auth_views.password_reset_done,
        {'template_name': 'registration/password_reset_done_new.html'},
        name='wachtwoord_instellen_klaar'
    ),
    url(r'^bevestig-wachtwoord-herstel/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': reverse_lazy('herstel_wachtwoord_afgerond'), },
        name='bevestig_herstel'
    ),
    url(r'^bevestig-wachtwoord-instellen/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {
            'post_reset_redirect': reverse_lazy('herstel_wachtwoord_afgerond'),
            'template_name': 'registration/password_reset_confirm_new.html',
        },
        name='bevestig_instellen'
        ),
    url(r'^wachtwoord-herstel-afgerond/',
        auth_views.password_reset_complete,
        name='herstel_wachtwoord_afgerond',
    ),
    url(r'^wachtwoord-instellen-afgerond/',
        auth_views.password_reset_complete,
        {'template_name': 'registration/password_reset_complete_new.html'},
        name='herstel_wachtwoord_afgerond',
        ),
    url(r'^api/', include(router.urls)),

]

urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]