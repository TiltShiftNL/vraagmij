from django.views.generic import TemplateView
from django.views.generic import *
from .forms import *
from django.urls import reverse, reverse_lazy
from django import forms
from django.db import transaction
from django.shortcuts import get_object_or_404

class Homepage(TemplateView):
    template_name = 'homepage.html'


class Entry(TemplateView):
    template_name = 'entry.html'


class RegelingView(CreateView):
    form_class = RegelingModelForm
    template_name = 'entry.html'
    regeling = None

    success_url = '.'

    voorwaarden = []

    def add_voorwaarde(self, voorwaarde):
        if self.regeling:
            v = Voorwaarde(titel=voorwaarde, regeling=self.regeling)
            return v.save()
        return


    def get_context_data(self, **kwargs):


        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('entry')

    def form_valid(self, form):
        #print(self.request.POST)
        self.regeling = form.save(True)
        #print(self.request.POST.getlist('voorwaarde', 'no voorwaarde'))
        voorwaarden = self.request.POST.getlist('voorwaarde', [])
        voorwaarden = [self.add_voorwaarde(v) for v in voorwaarden]
        print(voorwaarden)

        return super().form_valid(form)


class RegelingList(ListView):
    model = Regeling


class RegelingCreate(CreateView):
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


class RegelingUpdate(UpdateView):
    model = Regeling
    fields = ['titel', 'samenvatting', 'bron', 'startdatum', 'einddatum']
    #form_class = RegelingModelForm
    success_url = reverse_lazy('regelingen')

    def get_success_url(self):
        return reverse_lazy('update_regeling', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        print(self.object)
        print(Voorwaarde.objects.filter(regeling=self.object))
        if self.request.POST:
            data['voorwaarde'] = VoorwaardeFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['voorwaarde'] = VoorwaardeFormSet(instance=self.object)
        print(data)
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



