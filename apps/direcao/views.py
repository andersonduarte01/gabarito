from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import UserCreationDirecao
from .models import DirecaoEscolar
from ..core.models import Usuario
from ..escola.models import UnidadeEscolar
from ..perfil.models import Endereco


class CadDirecao(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = DirecaoEscolar
    form_class = UserCreationDirecao
    template_name = 'direcao/direcao_form.html'
    success_message = 'Membro da direção escolar cadastrado com sucesso.'
    success_url = reverse_lazy('direcao:lista_direcao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        funcionario = form.save(commit=False)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        funcionario.escola = escola
        funcionario.is_funcionario = True
        funcionario.save()
        return super().form_valid(form)


class DirecaoLista(LoginRequiredMixin, ListView):
    model = DirecaoEscolar
    template_name = 'direcao/lista_form.html'

    def get_queryset(self):
        return DirecaoEscolar.objects.filter(escola=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class EditarDirecao(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Usuario
    fields = ('email', 'nome')
    success_message = 'Informações do usuário atualizadas.'
    template_name = 'direcao/editarusuario_direcao.html'
    success_url = reverse_lazy('direcao:lista_direcao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = DirecaoEscolar.objects.get(pk=self.kwargs['pk'])
        return context


class EnderecoEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Endereco
    fields = '__all__'
    success_message = 'Endereço atualizado com sucesso'
    template_name = 'direcao/editar_endereco.html'
    success_url = reverse_lazy('direcao:lista_direcao')

    def get_object(self, queryset=None):
        funcionario = DirecaoEscolar.objects.get(pk=self.kwargs['pk'])
        return Endereco.objects.get(pk=funcionario.endereco.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = DirecaoEscolar.objects.get(pk=self.kwargs['pk'])
        return context


class EnderecoAdicionar(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Endereco
    fields = '__all__'
    success_message = 'Endereço adicionado com sucesso'
    template_name = 'direcao/adicionar_endereco.html'
    success_url = reverse_lazy('direcao:lista_direcao')

    def form_valid(self, form):
        endereco = form.save()
        funcionario = DirecaoEscolar.objects.get(pk=self.kwargs['pk'])
        funcionario.endereco = endereco
        funcionario.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = DirecaoEscolar.objects.get(pk=self.kwargs['pk'])
        return context

