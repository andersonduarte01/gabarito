from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from .forms import SalaForm
from .models import Sala


_TIPOS_GESTAO = [UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]


class ListaSalas(PermissaoRequiredMixin, ListView):
    model = Sala
    template_name = 'sala/lista_salas.html'
    context_object_name = 'salas'
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        return (
            Sala.objects
            .filter(escola=self.request.escola)
            .select_related('ano', 'ano_letivo')
            .order_by('descricao')
        )


class AdicionarSala(PermissaoRequiredMixin, SuccessMessageMixin, CreateView):
    model = Sala
    form_class = SalaForm
    template_name = 'sala/form_sala.html'
    success_message = 'Sala cadastrada com sucesso.'
    success_url = reverse_lazy('sala:lista_salas')
    permissao_tipos = _TIPOS_GESTAO

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['escola'] = self.request.escola
        return kwargs

    def form_valid(self, form):
        form.instance.escola = self.request.escola
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Adicionar Sala'
        return ctx


class EditarSala(PermissaoRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Sala
    form_class = SalaForm
    template_name = 'sala/form_sala.html'
    success_message = 'Sala atualizada com sucesso.'
    success_url = reverse_lazy('sala:lista_salas')
    permissao_tipos = _TIPOS_GESTAO

    def get_object(self, queryset=None):
        return get_object_or_404(Sala, pk=self.kwargs['pk'], escola=self.request.escola)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['escola'] = self.request.escola
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar — {self.object.descricao}'
        return ctx


class DeletarSala(PermissaoRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Sala
    template_name = 'sala/confirmar_remocao.html'
    success_message = 'Sala removida com sucesso.'
    success_url = reverse_lazy('sala:lista_salas')
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def get_object(self, queryset=None):
        return get_object_or_404(Sala, pk=self.kwargs['pk'], escola=self.request.escola)
