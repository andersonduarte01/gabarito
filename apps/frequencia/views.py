import calendar
import datetime
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy, reverse

from . import models
from .gerarPlanilha import criarFrequenciaDiaria
from django.views.generic import UpdateView, CreateView, ListView, DeleteView, TemplateView
from datetime import datetime
from .forms import FrequenciaAlunoForm, RegistroForm, RelatorioForm

from ..aluno.models import Aluno
from ..escola.models import UnidadeEscolar
from ..escola.traduzir import converter
from ..funcionario.models import Professor
from ..sala.models import Sala
from .models import Frequencia, FrequenciaAluno, Registro, Relatorio, Periodo


class FreqDiaria(UpdateView):
    model = Frequencia
    fields = ('presentes', 'observacao')
    template_name = 'frequencia/freqdiaria.html'
    success_url = reverse_lazy('frequencia:freq')

    def get_queryset(self):
        return Frequencia.objects.filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(FreqDiaria, self).get_context_data(**kwargs)
        data01 = Frequencia.objects.get(pk=self.kwargs['pk'])
        sala = Sala.objects.get(pk=data01.sala.id)
        context['data'] = data01.data
        context['sala'] = sala
        return context


def frequencia_diaria(request, cal, sala_id):
    x = cal.replace("-", "/")
    data = datetime.strptime(x, '%Y/%m/%d')
    sala = Sala.objects.get(pk=sala_id)
    escola = None
    professor = ''
    if request.user.is_professor:
        professor = Professor.objects.get(usuario_ptr=request.user)
        escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
    else:
        escola = UnidadeEscolar.objects.get(pk=sala.escola.pk)

    alunos = Aluno.objects.filter(sala=sala)
    criarFrequenciaDiaria(alunos=alunos, data=data)
    frequencias = FrequenciaAluno.objects.filter(data=data, aluno__in=alunos).order_by()
    RespostasFormSet = modelformset_factory(FrequenciaAluno, form=FrequenciaAlunoForm, extra=0)

    if request.method == 'POST':
        formset = RespostasFormSet(request.POST, request.FILES, queryset=frequencias,)
        if formset.is_valid():
            formset.save()
            url = reverse_lazy('escola:painel_planilha_00', kwargs={'slug': escola.slug, 'data': data.date()})
            return HttpResponseRedirect(url)
    else:
        formset = RespostasFormSet(queryset=frequencias)
    return render(request, 'frequencia/frequencia_aluno.html',
                  {'formset': formset, 'escola': escola, 'professor': professor, 'sala': sala, 'data': data.date()})


class RegistroAdd(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Registro
    form_class = RegistroForm
    success_message = 'Registro adicionado com sucesso!'
    template_name = 'frequencia/registro_add.html'

    def get_success_url(self):
        professor = get_object_or_404(Professor, usuario_ptr=self.request.user)
        data = self.kwargs['data']
        return reverse_lazy('escola:painel_planilha_00', kwargs={'slug': professor.escola.slug, 'data': data})

    def form_valid(self, form):
        registro = form.save(commit=False)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        registro.sala = sala
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        registro.professor = professor
        registro.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)

        sala = Sala.objects.get(pk=self.kwargs['pk'])
        contexto['professor'] = professor
        contexto['escola'] = escola
        contexto['data'] = self.kwargs['data']
        contexto['sala'] = sala
        return contexto


class RegistroUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Registro
    form_class = RegistroForm
    success_message = 'Registro alterado com sucesso!'
    template_name = 'frequencia/registro_up.html'

    def get_success_url(self):
        professor = get_object_or_404(Professor, usuario_ptr=self.request.user)
        data = self.kwargs['data']
        return reverse_lazy('escola:painel_planilha_00', kwargs={'slug': professor.escola.slug, 'data': data})

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)

        sala = Sala.objects.get(pk=self.object.sala.pk)
        contexto['professor'] = professor
        contexto['escola'] = escola
        contexto['data'] = self.kwargs['data']
        contexto['sala'] = sala
        return contexto


class DeletarRegistro(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Registro
    success_message = 'Registro removido com sucesso!'

    def get_object(self, queryset=None):
        return Registro.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('frequencia:registro_mes', kwargs={'pk': self.object.sala.pk, 'mes': self.object.data.month})


class RegistroMesesSalas(LoginRequiredMixin, ListView):
    template_name = 'frequencia/meses_salas.html'
    context_object_name = 'meses'

    def get_queryset(self):
        nome_meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',
            4: 'Abril', 5: 'Maio',  6: 'Junho', 7: 'Julho',
            8: 'Agosto', 9: 'Setembro', 10: 'Outubro',
            11: 'Novembro', 12: 'Dezembro'
        }

        registros_com_mes = Registro.objects.annotate(mes_registro=ExtractMonth('data'))
        meses_unicos = registros_com_mes.values_list('mes_registro', flat=True).distinct()
        nomes_e_numeros_meses = [(mes, nome_meses[mes]) for mes in meses_unicos]
        nomes_e_numeros_meses = sorted(nomes_e_numeros_meses, key=lambda x: x[0])
        return nomes_e_numeros_meses

    def get_context_data(self, *, object_list=None, **kwargs):
        contexto = super().get_context_data(**kwargs)
        professor = 'Sem Professor'
        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user.pk)

        salas = Sala.objects.filter(escola=escola)

        contexto['escola'] = escola
        contexto['professor'] = professor
        contexto['salas'] = salas
        return contexto


class RegistroMesSala(LoginRequiredMixin, ListView):
    template_name = 'frequencia/mes_sala.html'
    context_object_name = 'mes'

    def get_queryset(self):
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        return Registro.objects.filter(data__month=self.kwargs['mes'], sala=sala).order_by('data')

    def get_context_data(self, *, object_list=None, **kwargs):
        contexto = super().get_context_data(**kwargs)
        professor = 'vazio'
        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user.pk)

        sala = Sala.objects.get(pk=self.kwargs['pk'])

        contexto['escola'] = escola
        contexto['professor'] = professor
        contexto['sala'] = sala
        return contexto


class RelatorioAdd(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Relatorio
    form_class = RelatorioForm
    success_message = 'Relatorio adicionado com sucesso!'
    template_name = 'frequencia/relatorio_add.html'

    def get_success_url(self):
        return reverse('frequencia:alunos_relatorios',
                       kwargs={'pk': self.object.aluno.sala.pk, 'bimestre': self.object.periodo})

    def form_valid(self, form):
        relatorio = form.save(commit=False)
        aluno = Aluno.objects.get(pk=self.kwargs['pk'])
        relatorio.aluno = aluno
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        relatorio.professor = professor
        periodo = Periodo.objects.get(periodo=self.kwargs['bimestre'])
        relatorio.periodo = periodo
        relatorio.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        aluno = Aluno.objects.get(pk=self.kwargs['pk'])

        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)

        contexto['professor'] = professor
        contexto['escola'] = escola
        contexto['aluno'] = aluno
        contexto['bimestre'] = self.kwargs['bimestre']
        return contexto


class RelatorioUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Relatorio
    form_class = RelatorioForm
    success_message = 'Relatório alterado com sucesso!'
    template_name = 'frequencia/relatorio_up.html'
    context_object_name = 'relatorio'

    def get_success_url(self):
        return reverse('frequencia:alunos_relatorios',
                       kwargs={'pk': self.object.aluno.sala.pk, 'bimestre': self.object.periodo})

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)

        sala = Sala.objects.get(pk=self.object.aluno.sala.pk)
        contexto['professor'] = professor
        contexto['escola'] = escola
        contexto['sala'] = sala
        return contexto


class PainelRelatorios(LoginRequiredMixin, TemplateView):
    template_name = 'frequencia/painel_relatorios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = ''
        escola = None
        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)

        salas = Sala.objects.filter(escola=escola)

        salas_relatorios = []
        for sala in salas:

            sala_relatorio = []

            sala_relatorio.append(sala)
            try:
                periodo = Periodo.objects.get(periodo=self.kwargs['bimestre'])
                relatorios = Relatorio.objects.filter(aluno__sala=sala, periodo=periodo).count()
                sala_relatorio.append(relatorios)
            except:
                relatorios = 0
                sala_relatorio.append(relatorios)

            salas_relatorios.append(sala_relatorio)

        context['salas'] = salas_relatorios
        context['texto_bimestre'] = self.kwargs['bimestre'].replace('_', ' ')
        context['bimestre'] = self.kwargs['bimestre']
        context['escola'] = escola
        context['professor'] = professor
        return context


class ListaAlunosrelatorios(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'frequencia/alunos_relatorios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        alunos = Aluno.objects.filter(sala=sala).order_by('nome')
        professor = ''

        alunos_relatorios = []
        for aluno in alunos:
            aluno_relatorio = []
            aluno_relatorio.append(aluno)
            try:
                periodo = Periodo.objects.get(periodo=self.kwargs['bimestre'])
                relatorio = Relatorio.objects.get(aluno=aluno, periodo=periodo)
                aluno_relatorio.append(relatorio)
            except:
                relatorio = None
                aluno_relatorio.append(relatorio)

            alunos_relatorios.append(aluno_relatorio)

        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user.pk)

        context['bimestre'] = self.kwargs['bimestre']
        context['sala'] = sala
        context['alunos'] = alunos_relatorios
        context['escola'] = escola
        context['professor'] = professor

        return context
