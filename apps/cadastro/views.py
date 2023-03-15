from django.shortcuts import render
from django.views.generic import CreateView

from ..cadastro.models import Cadastro


# Create your views here.

class Cadastrar(CreateView):
    model = Cadastro
    fields = ('nome_escola', 'inep', 'email', 'contato', 'zona', 'rua', 'numero', 'complemento', 'bairro')
    template_name = 'cadastro/cadastro_add.html'
    success_url = '/'

