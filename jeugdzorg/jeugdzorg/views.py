from django.views.generic import TemplateView
from django.views.generic import *
from .forms import *
from django.urls import reverse, reverse_lazy
from django import forms
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin


class RegelingList(ListView):
    model = Regeling


class RegelingCreate(CreateView, LoginRequiredMixin):
    model = Regeling
    fields = ['titel', 'samenvatting', 'bron', 'startdatum', 'einddatum']
    success_url = reverse_lazy('regelingen')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['voorwaarde'] = VoorwaardeFormSet(self.request.POST)
        else:
            data['voorwaarde'] = VoorwaardeFormSet()
        return data

    def get_success_url(self):
        return reverse_lazy('update_regeling', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        context = self.get_context_data()
        voorwaarde = context['voorwaarde']
        with transaction.atomic():
            self.object = form.save()

            if voorwaarde.is_valid():
                voorwaarde.instance = self.object
                voorwaarde.save()
        return super(RegelingCreate, self).form_valid(form)


class RegelingUpdate(UpdateView, LoginRequiredMixin):
    model = Regeling
    fields = ['titel', 'samenvatting', 'bron', 'startdatum', 'einddatum']
    #form_class = RegelingModelForm
    success_url = reverse_lazy('regelingen')

    def get_success_url(self):
        if self.request.POST.get('submit'):
            return self.request.POST.get('submit')
        return reverse_lazy('update_regeling', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['voorwaarde'] = VoorwaardeFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['voorwaarde'] = VoorwaardeFormSet(instance=self.object)
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



