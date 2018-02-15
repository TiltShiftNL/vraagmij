from django.views.generic import TemplateView
from django.views.generic import *
from .forms import *
from django.urls import reverse, reverse_lazy
from django import forms
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
import sys
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import select_template


class ConfigView(LoginRequiredMixin, TemplateView):
    template_name = 'snippets/config.html'


class RegelingList(ListView):
    model = Regeling

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        template = select_template([
            'snippets/regeling_list_%s.html' % self.request.GET.get('beeld', 'alfabet'),
            'snippets/regeling_list_alfabet.html'
        ])
        data['doelen'] = Doel.objects.all()
        data['list_template'] = template
        return data


class RegelingCreate(LoginRequiredMixin, CreateView):
    model = Regeling
    fields = ['titel', 'samenvatting', 'bron', 'bron_url', 'startdatum', 'einddatum']
    success_url = reverse_lazy('regelingen')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        doelen = Doel.objects.all()
        doelen_added = []
        post = self.request.POST
        if post:
            data['voorwaarde'] = VoorwaardeFormSet(self.request.POST)
            for doel in doelen:
                if post.getlist('regeling-doel-input-%s' % doel.id)[0] == 'true':
                    doelen_added.append(doel.id)
        else:
            data['voorwaarde'] = VoorwaardeFormSet()

        data['doelen'] = doelen
        data['doelen_added'] = doelen_added
        return data

    def get_success_url(self):
        if self.request.POST.get('submit'):
            return self.request.POST.get('submit')
        return reverse_lazy('update_regeling', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        context = self.get_context_data()
        voorwaarde = context['voorwaarde']
        post = self.request.POST
        doelen = Doel.objects.all()
        with transaction.atomic():
            self.object = form.save()
            for doel in doelen:
                if post.getlist('regeling-doel-input-%s' % doel.id)[0] == 'true':
                    self.object.doelen.add(doel)
                else:
                    self.object.doelen.remove(doel)
            if voorwaarde.is_valid():
                voorwaarde.instance = self.object
                voorwaarde.save()
        return super(RegelingCreate, self).form_valid(form)


class RegelingUpdate(LoginRequiredMixin, UpdateView):
    model = Regeling
    fields = ['titel', 'samenvatting', 'bron', 'bron_url', 'startdatum', 'einddatum']
    success_url = reverse_lazy('regelingen')

    def get_success_url(self):
        if self.request.POST.get('submit'):
            return self.request.POST.get('submit')
        return reverse_lazy('update_regeling', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        doelen = Doel.objects.all()
        doelen_added = [d.id for d in self.object.doelen.all()]
        post = self.request.POST
        if post:
            data['voorwaarde'] = VoorwaardeFormSet(self.request.POST, self.request.FILES, instance=self.object)
            for doel in doelen:
                if post.getlist('regeling-doel-input-%s' % doel.id)[0] == 'true':
                    self.object.doelen.add(doel)
                else:
                    self.object.doelen.remove(doel)


        else:
            data['voorwaarde'] = VoorwaardeFormSet(instance=self.object)
        data['doelen'] = doelen
        data['doelen_added'] = doelen_added
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        voorwaarde = context['voorwaarde']
        with transaction.atomic():
            self.object = form.save()
            if voorwaarde.is_valid():
                voorwaarde.instance = self.object
                voorwaarde.save()
        return super(RegelingUpdate, self).form_valid(form)


@staff_member_required
def dump_jeugdzorg(request):
    sysout = sys.stdout
    fname = "%s.json" % ('jeugdzorg')
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=%s' % fname

    sys.stdout = response
    call_command('dumpdata', 'jeugdzorg', '--indent=4')
    sys.stdout = sysout
    return response


@staff_member_required
def load_jeugdzorg(request):
    if request.method == 'POST':
        form = UploadJeugdzorgFixtureFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('%s?success=1' % reverse('loadjeugdzorg'))
    else:
        form = UploadJeugdzorgFixtureFileForm()
    return render(request, 'snippets/upload_fixture.html', {'form': form})



