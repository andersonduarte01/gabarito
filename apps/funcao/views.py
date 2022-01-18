from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Funcao
from ..funcionario.models import Funcionario
from ..escola.models import UnidadeEscolar


class ListaFuncao(LoginRequiredMixin, ListView):
    model = Funcao
    template_name = 'funcao/lista_funcao.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context

    def get_queryset(self):
        return Funcao.objects.filter(escola=self.request.user)


class AdicionarFuncao(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Funcao
    fields = ('funcao', 'codigo')
    template_name = 'funcao/adicionar_funcao.html'
    success_message = 'Função adicionada com sucesso'
    success_url = reverse_lazy('funcao:lista_funcoes')

    def form_valid(self, form):
        funcao = form.save(commit=False)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        funcao.escola = escola
        funcao.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class AtualizarFuncao(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Funcao
    fields = ('codigo', 'funcao')
    template_name = 'funcao/editar_funcao.html'
    success_message = "Função atualizada com sucesso"
    success_url = reverse_lazy('funcao:lista_funcoes')

    def get_object(self, queryset=None):
        return Funcao.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class RemoverFuncao(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Funcao
    success_message = 'Função removida com sucesso!'
    success_url = reverse_lazy('funcao:lista_funcoes')

    def get_object(self, queryset=None):
        funcao = Funcao.objects.get(pk=self.kwargs['pk'])
        return funcao
