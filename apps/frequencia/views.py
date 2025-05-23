import calendar
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now

from ..escola.forms import FiltroMesForm
from . import models
from .gerarPlanilha import criarFrequenciaDiaria
from django.views.generic import UpdateView, CreateView, ListView, DeleteView, TemplateView, FormView
from datetime import datetime
from .forms import FrequenciaAlunoForm, RegistroForm, RelatorioForm, RegistroUpdateForm

from ..aluno.models import Aluno
from ..escola.models import UnidadeEscolar
from ..escola.traduzir import converter
from ..funcionario.models import Professor
from ..sala.models import Sala
from .models import Frequencia, FrequenciaAluno, Registro, Relatorio, Periodo


class RegistroMesesSalas(LoginRequiredMixin, FormView):
    template_name = 'frequencia/meses_salas.html'
    form_class = FiltroMesForm
    registros_filtrados = None  # Adiciona um atributo para armazenar os registros

    def form_valid(self, form):
        mes = int(form.cleaned_data['mes'])
        sala = get_object_or_404(Sala, id=self.kwargs['sala_id'])
        self.registros_filtrados = Registro.objects.filter(
            sala=sala,
            data__month=mes,
            data__year=now().year
        )
        context = self.get_context_data(form=form, registros=self.registros_filtrados)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        sala = get_object_or_404(Sala, id=self.kwargs['sala_id'])
        context['escola'] = escola
        context['form'] = context.get('form') or self.form_class(initial={'mes': now().month})
        context['sala'] = sala

        if self.registros_filtrados is not None:
            context['registros'] = self.registros_filtrados
        else:
            registros = Registro.objects.filter(
                sala=sala,
                data__month=now().month,
                data__year=now().year
            )
            context['registros'] = registros

        return context


class RelatorioAdd(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Relatorio
    form_class = RelatorioForm
    success_message = 'Relatorio adicionado com sucesso!'
    template_name = 'frequencia/relatorio_add.html'

    def get_success_url(self):
        return reverse('funcionario:alunos_relatorios',
                       kwargs={'pk': self.object.aluno.sala.pk, 'bimestre': self.object.periodo, 'slug':self.object.aluno.sala.escola.slug})

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

        professor = Professor.objects.get(usuario_ptr=self.request.user)
        contexto['professor'] = professor
        contexto['escola'] = get_object_or_404(UnidadeEscolar, pk=professor.escola.pk)
        contexto['aluno'] = get_object_or_404(Aluno, pk=self.kwargs['pk'])
        contexto['bimestre'] = self.kwargs['bimestre']
        return contexto


class RelatorioUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Relatorio
    form_class = RelatorioForm
    success_message = 'Relatório alterado com sucesso!'
    template_name = 'frequencia/relatorio_up.html'
    context_object_name = 'relatorio'


    def get_success_url(self):
        return reverse('funcionario:alunos_relatorios',
                       kwargs={'pk': self.object.aluno.sala.pk, 'bimestre': self.object.periodo,
                               'slug': self.object.aluno.sala.escola.slug})

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        professor = get_object_or_404(Professor, usuario_ptr=self.request.user)
        contexto['professor'] = professor
        contexto['escola'] = get_object_or_404(UnidadeEscolar, pk=professor.escola.pk)
        contexto['sala'] = get_object_or_404(Sala, pk=self.object.aluno.sala.pk)
        return contexto


class ProfessorRegistroMesesSalas(LoginRequiredMixin, FormView):
    template_name = 'frequencia/prof_meses_salas.html'
    form_class = FiltroMesForm
    registros_filtrados = None  # Adiciona um atributo para armazenar os registros

    def form_valid(self, form):
        mes = int(form.cleaned_data['mes'])
        sala = get_object_or_404(Sala, id=self.kwargs['sala_id'])
        self.registros_filtrados = Registro.objects.filter(
            sala=sala,
            data__month=mes,
            data__year=now().year
        )
        context = self.get_context_data(form=form, registros=self.registros_filtrados)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = get_object_or_404(Sala, id=self.kwargs['sala_id'])
        escola = get_object_or_404(UnidadeEscolar, pk=sala.escola.pk)
        context['escola'] = escola
        context['form'] = context.get('form') or self.form_class(initial={'mes': now().month})
        context['sala'] = sala

        if self.registros_filtrados is not None:
            context['registros'] = self.registros_filtrados
        else:
            registros = Registro.objects.filter(
                sala=sala,
                data__month=now().month,
                data__year=now().year
            ).order_by('data')
            context['registros'] = registros

        return context


class RegistroAdd(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Registro
    form_class = RegistroForm
    success_message = 'Registro adicionado com sucesso!'
    template_name = 'frequencia/registro_add.html'

    def get_success_url(self):
        return reverse('frequencia:prof_relatorio_meses', kwargs={'sala_id': self.kwargs['pk']})

    def form_valid(self, form):
        registro = form.save(commit=False)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        registro.professor = professor
        registro.sala = sala
        registro.save()
        return super().form_valid(form)

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
        contexto['sala'] = sala
        return contexto