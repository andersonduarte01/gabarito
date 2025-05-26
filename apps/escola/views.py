from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import date
from datetime import datetime
from django.db.models.functions import ExtractMonth
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views.generic import TemplateView, UpdateView, ListView, RedirectView, FormView, CreateView

from .forms import FiltroMesForm, EscolaForm, EnderecoForm1, UsuarioForm
from .models import UnidadeEscolar, EnderecoEscolar, AnoLetivo
from ..aluno.models import Aluno
from ..avaliacao.correcao import alunos_prova
from ..avaliacao.models import Avaliacao, Gabarito
from ..core.models import Usuario
from ..frequencia.models import Frequencia, FrequenciaAluno, Registro, Periodo, Relatorio
from ..funcionario.models import Professor
from ..sala.models import Sala
from .traduzir import converter
from .gerarPlanilhaFrequencia import dias_mes, presentesDia, dias, percentual

class Redireciona(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):

        user = self.request.user
        if user.is_administrator:
            return reverse_lazy('escola:painel_adm')
        elif user.is_professor:
            return reverse_lazy('funcionario:dash_professor')
        elif user.is_aluno:
            return reverse_lazy('aluno:dash_aluno')
        elif user.is_funcionario:
            return reverse_lazy('funcionario:dash_funcionario')
        return reverse_lazy('escola:dash_escola')


class DashAdmin(LoginRequiredMixin, TemplateView):
    template_name = 'escola/administrador_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escolas = UnidadeEscolar.objects.all()
        context['escolas'] = escolas
        return context


class DashEscola(LoginRequiredMixin, TemplateView):
    template_name = 'escola/escola_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        ano_corrente = AnoLetivo.objects.get(corrente=True)
        salas = Sala.objects.filter(escola=escola, ano_letivo=ano_corrente).order_by('ano')
        context['escola'] = escola
        context['salas'] = salas
        context['data'] = now()
        return context


class EditarEscola(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = EscolaForm
    model = UnidadeEscolar
    success_message = 'Informações atualizadas com sucesso!'
    template_name = 'escola/editarescolar_form.html'
    success_url = reverse_lazy('escola:dash_escola')
    context_object_name = 'escola'

    def get_object(self, queryset=None):
        return get_object_or_404(UnidadeEscolar, pk=self.kwargs['pk'])


class EditarEndereco(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = EnderecoForm1
    model = EnderecoEscolar
    template_name = 'escola/editarendereco_form.html'
    context_object_name = 'escola'
    success_message = 'Endereço atualizado com sucesso!'
    success_url = reverse_lazy('escola:dash_escola')

    def get_object(self, queryset=None):
        return get_object_or_404(EnderecoEscolar, endereco=self.request.user)


class EditarUsuario(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = UsuarioForm
    model = Usuario
    success_message = 'Informações atualizadas com sucesso!'
    template_name = 'escola/editarusuario_form.html'
    success_url = reverse_lazy('escola:dash_escola')


class UnidAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'escola/adm_unidade_alunos.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        return Aluno.objects.filter(sala_id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        sala = get_object_or_404(Sala, id=self.kwargs['id'])
        context['escola'] = escola
        context['sala'] = sala
        return context


class ListAlunos(LoginRequiredMixin, CreateView):
    model = Aluno
    fields = ('nome', 'data_nascimento', 'sexo')
    template_name = 'escola/lista_alunos.html'
    context_object_name = 'alunos'

    def form_valid(self, form):
        aluno = form.save(commit=False)
        sala = Sala.objects.get(id=self.kwargs['id'])
        sala.total_alunos += 1
        sala.save()
        aluno.sala = sala
        aluno.save()
        return super(ListAlunos, self).form_valid(form)

    def get_success_url(self):
        return reverse('escola:unidade_sala_alunos', kwargs={'id': self.get_context_data()['sala'].id,
                                                             'slug': self.get_context_data()['escola'].slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['id'])
        alunos = Aluno.objects.filter(sala=sala).order_by('nome')
        escola = UnidadeEscolar.objects.get(pk=sala.escola.pk)
        context['sala'] = sala
        context['alunos'] = alunos
        context['escola'] = escola
        return context


class FrequenciaRelatorios(LoginRequiredMixin, TemplateView):
    template_name = 'escola/relatorio_frequencia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        context['escola'] = escola
        context['sala'] = sala
        return context