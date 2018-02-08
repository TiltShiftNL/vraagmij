from django.views.generic import TemplateView


class Homepage(TemplateView):
    template_name = 'homepage.html'

class Entry(TemplateView):
    template_name = 'entry.html'

class Entries(TemplateView):
    template_name = 'entries.html'