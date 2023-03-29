from django.shortcuts import render
from django.views.generic import CreateView, TemplateView

from ..cadastro.models import Cadastro
from ..core.models import Usuario


# Create your views here.

class Cadastrar(CreateView):
    model = Cadastro
    fields = ('nome_escola', 'inep', 'email', 'contato', 'zona', 'rua', 'numero', 'complemento', 'bairro')
    template_name = 'cadastro/cadastro_add.html'
    success_url = '/cadastro/sucesso/'


class CadastroSucess(TemplateView):
    template_name = 'cadastro/sucesso.html'
