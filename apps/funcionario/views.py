from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from .forms import UserCreationFuncionario, DesignarFuncaoForm
from .models import Funcionario
from ..core.models import Usuario
from ..escola.models import UnidadeEscolar
from ..funcao.models import Funcao
from ..perfil.models import Endereco, Pessoa


class CadastrarFuncionario(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Funcionario
    form_class = UserCreationFuncionario
    template_name = 'funcionario/adicionar_funcionario.html'
    success_message = 'Membro da direção escolar cadastrado com sucesso.'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

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


class EditarFuncionario(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Usuario
    fields = ('email', 'nome')
    success_message = 'Informações do usuário atualizadas.'
    template_name = 'funcionario/editar_funcionario.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class ListaFuncionarios(LoginRequiredMixin, ListView):
    model = Funcionario
    template_name = 'funcionario/lista_funcionarios.html'

    def get_queryset(self):
        return Funcionario.objects.filter(escola=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class EnderecoEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Endereco
    fields = '__all__'
    success_message = 'Endereço atualizado com sucesso'
    template_name = 'funcionario/editar_endereco.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_object(self, queryset=None):
        funcionario = Funcionario.objects.get(pk=self.kwargs['pk'])
        return Endereco.objects.get(pk=funcionario.endereco.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class EnderecoAdicionar(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Endereco
    fields = '__all__'
    success_message = 'Endereço adicionado com sucesso'
    template_name = 'funcionario/adicionar_endereco.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def form_valid(self, form):
        endereco = form.save()
        funcionario = Funcionario.objects.get(pk=self.kwargs['pk'])
        funcionario.endereco = endereco
        funcionario.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class PerfilAdicionar(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Pessoa
    fields = '__all__'
    success_message = 'Perfil adicionado com sucesso'
    template_name = 'funcionario/adicionar_perfil.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def form_valid(self, form):
        perfil = form.save()
        funcionario = Funcionario.objects.get(pk=self.kwargs['pk'])
        funcionario.perfil = perfil
        funcionario.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class EditarPerfil(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Pessoa
    fields = '__all__'
    success_message = 'Perfil atualizado com sucesso'
    template_name = 'funcionario/editar_perfil.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_object(self, queryset=None):
        funcionario = Funcionario.objects.get(pk=self.kwargs['pk'])
        return Pessoa.objects.get(pk=funcionario.perfil.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class DesignarFuncao(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Funcionario
    form_class = DesignarFuncaoForm
    success_message = 'Função designada com sucesso'
    template_name = 'funcionario/designar_funcao.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_object(self, queryset=None):
        return Funcionario.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        funcao = Funcao.objects.filter(escola=self.request.user)
        context['funcao'] = funcao
        return context


class DeletarDirecao(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Funcionario
    success_message = 'Funcionário removido com sucesso!'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_object(self, queryset=None):
        return Funcionario.objects.get(pk=self.kwargs['pk'])