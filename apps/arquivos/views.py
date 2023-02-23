from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, ListView, DeleteView, UpdateView

from .models import Arquivo, Categoria, Livro
from ..core.models import Usuario
from ..escola.models import UnidadeEscolar


# Create your views here.

class Arquivos(LoginRequiredMixin, SuccessMessageMixin,CreateView):
    model = Arquivo
    fields = ('titulo', 'descricao', 'pdf', 'publico')
    template_name = 'arquivos/arquivo.html'
    success_message = 'Arquivo adicionado com sucesso!'
    success_url = '/pdf/'

    def form_valid(self, form):
        arquivo = form.save(commit=False)
        usuario = Usuario.objects.get(pk=self.request.user.id)
        arquivo.escola = usuario
        arquivo.save()
        return super(Arquivos, self).form_valid(form)


class CategoriaAdd(LoginRequiredMixin, SuccessMessageMixin,CreateView):
    model = Categoria
    fields = ('categoria',)
    template_name = 'arquivos/categoria.html'
    success_message = 'Categoria adicionada com sucesso!'
    success_url = '/pdf/lista/categorias/'


class CategoriaList(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'arquivos/lista_categoria.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return Categoria.objects.all()


class LivroAdd(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Livro
    fields = ('titulo', 'descricao', 'categoria', 'autor', 'editora', 'ano_referencia', 'pdf')
    template_name = 'arquivos/livro.html'
    success_message = 'Livro adicionado com sucesso!'
    success_url = '/pdf/livro/'


class DeletarCategoria(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Categoria
    success_message = 'Categoria removida com sucesso!'

    def get_object(self, queryset=None):
        return Categoria.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('arquivos:lista_categoria')


class CategoriaEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Categoria
    fields = ('categoria',)
    template_name = 'arquivos/categoria_up.html'
    success_message = 'Categoria atualizada com sucesso!'

    def get_success_url(self):
        return reverse('arquivos:lista_categoria')


class LivroEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Livro
    fields = ('titulo', 'descricao', 'categoria', 'autor', 'editora', 'ano_referencia', 'pdf')
    template_name = 'arquivos/livro_up.html'

    def get_success_url(self):
        return reverse('core:arquivos')


class ArquivoEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Arquivo
    fields = ('titulo', 'descricao', 'pdf', 'publico')
    template_name = 'arquivos/arquivo_up.html'

    def get_success_url(self):
        return reverse('core:arquivos')


class DeletarLivro(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Livro
    success_message = 'Livro removido com sucesso!'

    def get_object(self, queryset=None):
        return Livro.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('core:biblioteca')


class DeletarArquivo(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Arquivo
    success_message = 'Arquivo removido com sucesso!'

    def get_object(self, queryset=None):
        return Arquivo.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('core:arquivos')