from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView

from ..arquivos.models import Arquivo, Livro
from ..blog.models import Video
from.forms import UserCreationForm
from ..sala.models import Ano


class Index(TemplateView):
    template_name = 'core/index.html'


class Contato(TemplateView):
    template_name = 'core/contate_nos.html'


class Sobre(TemplateView):
    template_name = 'core/sobre.html'


class Eventos(LoginRequiredMixin, TemplateView):
    template_name = 'core/tutoriais.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videos = Video.objects.all().order_by('-data_atualizada')
        context['videos'] = videos
        return context


class Biblioteca(TemplateView):
    template_name = 'core/biblioteca.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        infantil = []
        pre = []
        ano1 = []
        ano2 = []
        ano3 = []
        ano4 = []
        ano5 = []
        ano6 = []
        ano7 = []
        ano8 = []
        ano9 = []
        livros = Livro.objects.all().order_by('-data_modificacao')

        for periodo in livros:
            if periodo.ano_referencia.descricao == "Educação Infantil":
                infantil.append(periodo)
            elif periodo.ano_referencia.descricao == "Pré-Escola":
                pre.append(periodo)
            elif periodo.ano_referencia.descricao == '1º Ano':
                ano1.append(periodo)
            elif periodo.ano_referencia.descricao == "2º Ano":
                ano2.append(periodo)
            elif periodo.ano_referencia.descricao == "3º Ano":
                ano3.append(periodo)
            elif periodo.ano_referencia.descricao == "4º Ano":
                ano4.append(periodo)
            elif periodo.ano_referencia.descricao == "5º Ano":
                ano5.append(periodo)
            elif periodo.ano_referencia.descricao == "6º Ano":
                ano6.append(periodo)
            elif periodo.ano_referencia.descricao == "7º Ano":
                ano7.append(periodo)
            elif periodo.ano_referencia.descricao == "8º Ano":
                ano8.append(periodo)
            elif periodo.ano_referencia.descricao == "9º Ano":
                ano9.append(periodo)
            else:
                print('saiu sem anexar')

        context['infantil'] = infantil
        context['pre'] = pre
        context['ano1'] = ano1
        context['ano2'] = ano2
        context['ano3'] = ano3
        context['ano4'] = ano4
        context['ano5'] = ano5
        context['ano6'] = ano6
        context['ano7'] = ano7
        context['ano8'] = ano8
        context['ano9'] = ano9
        return context


class Arquivos(TemplateView):
    template_name = 'core/arquivos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        arquivos = Arquivo.objects.all().order_by('-data_modificacao')
        context['arquivos'] = arquivos
        return context


class PesquisarArquivo(ListView):
    model = Arquivo
    template_name = 'core/arquivos_resultado.html'
    context_object_name = 'arquivos'
    def get_queryset(self):
        query = self.request.GET.get("q")
        arquivos = Arquivo.objects.filter(Q(titulo__icontains=query))
        return arquivos


class PesquisarLivro(ListView):
    model = Livro
    template_name = 'core/biblioteca_resultado.html'
    context_object_name = 'livros'
    def get_queryset(self):
        query = self.request.GET.get("q")
        livros = Livro.objects.filter(Q(titulo__icontains=query))
        return livros


class PesquisarVideo(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'core/tutoriais_resultado.html'
    context_object_name = 'videos'
    def get_queryset(self):
        query = self.request.GET.get("q")
        videos = Video.objects.filter(Q(titulo__icontains=query))
        return videos


class AnoMateria(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'core/tutoriais00.html'
    context_object_name = 'videos'

    def get_queryset(self):
        periodo = self.kwargs['ano']
        ano=''
        print(periodo)
        if periodo == '1Ano':
            ano = Ano.objects.get(descricao='1º Ano')
        elif periodo == '2Ano':
            ano = Ano.objects.get(descricao='2º Ano')
        elif periodo == '3Ano':
            ano = Ano.objects.get(descricao='3º Ano')
        elif periodo == '4Ano':
            ano = Ano.objects.get(descricao='4º Ano')
        elif periodo == '5Ano':
            ano = Ano.objects.get(descricao='5º Ano')
        elif periodo == '6Ano':
            ano = Ano.objects.get(descricao='6º Ano')
        elif periodo == '7Ano':
            ano = Ano.objects.get(descricao='7º Ano')
        elif periodo == '8Ano':
            ano = Ano.objects.get(descricao='8º Ano')
        elif periodo == '9Ano':
            ano = Ano.objects.get(descricao='9º Ano')
        else:
            ano = Ano.objects.get(descricao='Educação Infantil')
        lista = Video.objects.filter(ano=ano, sigla=self.kwargs['sigla'])
        return lista
