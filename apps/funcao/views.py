from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from .models import Funcao


_TIPOS_GESTAO = [UsuarioEscola.DIRETOR]


class ListaFuncao(PermissaoRequiredMixin, ListView):
    model = Funcao
    template_name = 'funcao/lista_funcoes.html'
    context_object_name = 'funcoes'
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        return Funcao.objects.filter(escola=self.request.escola).order_by('funcao')


class AdicionarFuncao(PermissaoRequiredMixin, SuccessMessageMixin, CreateView):
    model = Funcao
    fields = ('funcao', 'codigo')
    template_name = 'funcao/form_funcao.html'
    success_message = 'Função adicionada com sucesso.'
    success_url = reverse_lazy('funcao:lista_funcoes')
    permissao_tipos = _TIPOS_GESTAO

    def form_valid(self, form):
        form.instance.escola = self.request.escola
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Adicionar Função'
        return ctx


class AtualizarFuncao(PermissaoRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Funcao
    fields = ('funcao', 'codigo')
    template_name = 'funcao/form_funcao.html'
    success_message = 'Função atualizada com sucesso.'
    success_url = reverse_lazy('funcao:lista_funcoes')
    permissao_tipos = _TIPOS_GESTAO

    def get_object(self, queryset=None):
        return get_object_or_404(Funcao, pk=self.kwargs['pk'], escola=self.request.escola)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar — {self.object.funcao}'
        return ctx


class RemoverFuncao(PermissaoRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Funcao
    template_name = 'funcao/confirmar_remocao.html'
    success_message = 'Função removida com sucesso.'
    success_url = reverse_lazy('funcao:lista_funcoes')
    permissao_tipos = _TIPOS_GESTAO

    def get_object(self, queryset=None):
        return get_object_or_404(Funcao, pk=self.kwargs['pk'], escola=self.request.escola)
