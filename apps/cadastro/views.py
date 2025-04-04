import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core import serializers
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from .forms import CadastramentoForm, UnicoForm, RGForm, EnderecoForm, ProfissionalForm
from ..cadastro.models import Cadastro, CadastroInicio, CadUnificado, RG, Endereco, Profissional
from ..core.models import Usuario
from ..escola.models import UnidadeEscolar


# Create your views here.

class Cadastrar(CreateView):
    model = Cadastro
    fields = ('nome_escola', 'inep', 'email', 'contato', 'zona', 'rua', 'numero', 'complemento', 'bairro')
    template_name = 'cadastro/cadastro_add.html'
    success_url = '/cadastro/sucesso/'


class CadastroInicio1(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = CadUnificado
    form_class = UnicoForm
    template_name = 'cadastro/cadastramentounico.html'
    success_message = 'Cadastramento iniciado com sucesso!'
    success_url = reverse_lazy('cadastro:cadastro_documentos')

    def form_valid(self, form):
        funcionario = form.save(commit=False)
        usuario = CadastroInicio.objects.get(email=self.request.user)
        funcionario.usuario = usuario
        funcionario.save()  # Salvando o usuário no banco
        return super().form_valid(form)


class Cadastramento(CreateView, SuccessMessageMixin):
    model = CadastroInicio
    form_class = CadastramentoForm
    template_name = 'cadastro/cadastramento.html'
    success_message = 'Cadastramento iniciado'
    success_url = reverse_lazy('cadastro:cadastro_inicio')

    def form_valid(self, form):
        funcionario = form.save(commit=False)
        password1 = form.cleaned_data["password1"]
        # Definindo a senha do usuário
        funcionario.set_password(password1)
        funcionario.is_funcionario = True
        funcionario.save()  # Salvando o usuário no banco

        user = authenticate(self.request, email=funcionario.email, password=password1)

        if user is not None:
            login(self.request, user)  # Realizando login do usuário
            return super().form_valid(form)
        else:
            form.add_error(None, 'Erro na autenticação.')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class RGView(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = RG
    form_class = RGForm
    template_name = 'cadastro/documentos.html'
    success_message = 'Informações cadastradas com sucesso!'
    success_url = reverse_lazy('cadastro:cadastro_endereco')

    def form_valid(self, form):
        docs = form.save()
        usuario = CadastroInicio.objects.get(email=self.request.user)
        #mudar filter para get
        funcionario = CadUnificado.objects.filter(usuario=usuario).first()
        funcionario.rg_cnh = docs
        funcionario.save()  # Salvando o usuário no banco
        return super().form_valid(form)


class Endereco(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = Endereco
    form_class = EnderecoForm
    template_name = 'cadastro/endereco.html'
    success_message = 'Endereço cadastrado com sucesso!'
    success_url = reverse_lazy('cadastro:cadastro_profissional')

    def form_valid(self, form):
        endereco = form.save()
        usuario = CadastroInicio.objects.get(email=self.request.user)
        # mudar filter para get
        funcionario = CadUnificado.objects.filter(usuario=usuario).first()
        funcionario.endereco = endereco
        funcionario.save()  # Salvando o usuário no banco
        return super().form_valid(form)


class Profissional1(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = Profissional
    form_class = ProfissionalForm
    template_name = 'cadastro/profissional.html'
    success_message = 'Cadastro finalizado!'
    success_url = reverse_lazy('cadastro:painel_user')

    def form_valid(self, form):
        prof = form.save()
        usuario = CadastroInicio.objects.get(email=self.request.user)
        # mudar filter para get
        funcionario = CadUnificado.objects.filter(usuario=usuario).first()
        funcionario.profissional = prof
        funcionario.save()  # Salvando o usuário no banco
        return super().form_valid(form)


class PainelUser(LoginRequiredMixin, TemplateView):
    template_name = 'cadastro/painel_user.html'
