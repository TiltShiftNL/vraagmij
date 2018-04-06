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
from django.views.generic import TemplateView
from rest_framework import routers
from .api import RegelingViewSet
from jeugdzorg.context_processors import app_settings

router = routers.DefaultRouter()
router.register(r'regelingen', RegelingViewSet, base_name='regeling')

testdata = {
        'site': {'hostname': 'hostdus'},
        'title': 'VraagMij',
        'content': 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui.',
}
# testdata.update(app_settings())
# print(testdata.get('SITE_INSTELLINGEN').site.domain)

def error_view(request):
    e = 1/0
    return HttpResponse('error')


urlpatterns = [

    # path('', CheckUserModel.as_view(), name='test'),
    # path('', ThemaList.as_view(), name='homepage'),
    path('', ThemaList.as_view(), {'sub_view': 'thema'}, name='homepage'),
    # path('', RegelingList.as_view(), {'sub_view': 'regeling'}, name='homepage'),
    path('regelingen/', RegelingList.as_view(), {'sub_view': 'regeling'}, name='regelingen'),
    path('regeling-maken/', RegelingCreate.as_view(), name='create_regeling'),
    path('regeling/<int:pk>/', RegelingDetail.as_view(), {'sub_view': 'regeling'}, name='detail_regeling'),
    path('themas/', ThemaList.as_view(), {'sub_view': 'thema'}, name='themas'),
    path('thema/<slug:slug>/', ThemaDetail.as_view(), {'sub_view': 'thema'}, name='detail_thema'),
    path('thema/<slug:slug>/regeling/<int:pk>/', RegelingDetail.as_view(), {'sub_view': 'thema'}, name='detail_thema_regeling'),
    path('contacten/', ProfielList.as_view(), {'sub_view': 'contact'}, name='contacten'),
    path('contact/<int:pk>/', ProfielDetail.as_view(), {'sub_view': 'contact'}, name='detail_contact'),
    path('profiel/bewerken/', ProfielUpdateView.as_view(), {'sub_view': 'contact'}, name='update_profiel'),

    path('profiel-connect/', ProfielConnectToggle.as_view(), name='profiel_connect'),

    path('login/', auth_views.login, {
        'authentication_form': LoginForm,
    }, name='login'),
    path('logout/', logout, name='logout'),

    path('gebruiker-registreren/', UserCreationView.as_view(), name='gebruiker_registreren'),
    url(r'^gebruiker-activeren/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        UserActivationView.as_view(),
        name='gebruiker_activeren'
    ),

    path('gebruikers-toevoegen/', GebruikersToevoegenView.as_view(), name='gebruikers_toevoegen'),
    path('gebruiker-uitnodigen/', GebruikerUitnodigenView.as_view(), name='gebruiker_uitnodigen'),

    path('event/add', EventView.as_view(), name='add_event'),

    path('admin/', admin.site.urls),
    path('admin/dumpjeugdzorg/', dump_jeugdzorg, name='dumpjeugdzorg'),
    path('admin/loadjeugdzorg/', load_jeugdzorg, name='loadjeugdzorg'),
    path('admin/logs/', ConfigView.as_view(), name='logs'),
    path('admin/rebuild-crontabs/', RebuildCrontabsView.as_view(), name='rebuild_crontabs'),
    path('admin/email-template/', TemplateView.as_view(template_name='email/update_mail.html'), testdata, name='email-template'),

    url('^', include('django.contrib.auth.urls')),

    path('zoek/', SearchView.as_view(), name='zoek'),
    # path('error/', error_view, name='error'),



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
        password_reset_confirm_new_user,
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