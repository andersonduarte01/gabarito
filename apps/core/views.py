from django.views.generic import TemplateView

from ..escola.models import UnidadeEscolar
from ..arquivos.models import Arquivo


class Index(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and (self.request.user.is_administrator is False):
            escola = UnidadeEscolar.objects.get(pk=self.request.user)
            context['school'] = escola
        return context


class Contato(TemplateView):
    template_name = 'core/contate_nos.html'


class Sobre(TemplateView):
    template_name = 'core/sobre.html'


class Noticias(TemplateView):
    template_name = 'core/noticias.html'


class Eventos(TemplateView):
    template_name = 'core/tutoriais.html'


class Biblioteca(TemplateView):
    template_name = 'core/biblioteca.html'


class Arquivos(TemplateView):
    template_name = 'core/arquivos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        arquivos = Arquivo.objects.all().order_by('-data_modificacao')
        context['arquivos'] = arquivos
        return context