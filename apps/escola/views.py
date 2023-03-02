from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
import datetime
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from .traduzir import converter
from .models import UnidadeEscolar, EnderecoEscolar
from ..core.models import Usuario
from ..sala.models import Sala
from .traduzir import converter
from .gerarPlanilhaFrequencia import criarFrequencia, dias_mes, presentesDia, dias


class Painel(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_controle_escola.html'

    def get_context_data(self, **kwargs):
        bool_m = False
        bool_t = False
        bool_i = False
        context = super().get_context_data(**kwargs)
        if self.request.user.is_administrator:
            escolas = UnidadeEscolar.objects.all()
            context['escolas'] = escolas
            return context
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)
            if Sala.objects.filter(turno='manha', escola=escola).exists():
                print('verdadeiro')
                bool_m = True
            if Sala.objects.filter(turno='tarde').exists():
                bool_t = True
            if Sala.objects.filter(turno='integral').exists():
                bool_i = True

            context['escola'] = escola
            context['manha'] = bool_m
            context['tarde'] = bool_t
            context['integral'] = bool_i
            return context


class PainelPlanilha(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_controle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        salas = Sala.objects.filter(escola=escola, turno=self.kwargs['turno']).order_by('ano')
        ano = datetime.date.today().year
        mes = datetime.date.today().month
        mes_atual = dias_mes(mes=mes, ano=ano)
        turma = []
        for sala in salas:
            freq = criarFrequencia(mes_atual, sala)
            turma.append(freq)
        context['mes'] = mes_atual
        mes01 = converter(mes_atual[0].month)
        context['turma'] = turma
        context['mes1'] = mes01
        context['escola'] = escola
        return context


class PainelEscola(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_escola.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(slug=self.kwargs['slug'])
        salas = Sala.objects.filter(escola=escola).order_by('ano')
        ano = datetime.date.today().year
        mes = datetime.date.today().month
        mes_atual = dias_mes(mes=mes, ano=ano)
        m = mes_atual[0].strftime('%m')
        m1 = converter(int(m))
        presentes = presentesDia(mes_atual, salas)
        context['escola'] = escola
        context['salas'] = salas
        context['mes'] = dias(mes_atual)
        context['mes_atual'] = m1
        context['alunos'] = presentes
        return context


class EditarEscola(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UnidadeEscolar
    fields = ('nome_escola', 'inep', 'cnpj', 'telefone', 'logo_escola')
    success_message = 'Informações da instituição atualizadas'
    template_name = 'escola/editarescolar_form.html'
    success_url = reverse_lazy('escola:painel_escola')

    def get_object(self, queryset=None):
        return UnidadeEscolar.objects.get(pk=self.kwargs['pk'])

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
