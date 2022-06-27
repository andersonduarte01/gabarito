from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from .models import UnidadeEscolar, EnderecoEscolar
from ..core.models import Usuario
from ..sala.models import Sala


class Painel(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_controle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        salas = Sala.objects.filter(escola=escola).order_by('ano')
        context['escola'] = escola
        context['salas'] = salas
        return context


class EditarEscola(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UnidadeEscolar
    fields = ('nome_escola', 'inep', 'cnpj', 'telefone', 'logo_escola')
    success_message = 'Informações da instituição atualizadas'
    template_name = 'escola/editarescolar_form.html'
    success_url = reverse_lazy('escola:painel_escola')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class EditarUsuario(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Usuario
    fields = ('email', 'nome')
    success_message = 'Informações do usuário atualizadas'
    template_name = 'escola/editarusuario_form.html'
    success_url = reverse_lazy('escola:painel_escola')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class EditarEndereco(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = EnderecoEscolar
    fields = ('rua', 'numero', 'complemento', 'bairro', 'cep', 'cidade', 'estado')
    template_name = 'escola/editarendereco_form.html'
    success_message = 'Endereço atualizado com sucesso!'
    success_url = reverse_lazy('escola:painel_escola')

    def get_object(self, queryset=None):
        return EnderecoEscolar.objects.get(endereco=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context
