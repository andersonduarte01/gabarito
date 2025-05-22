from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView, FormView

from .forms import UserCreationFuncionario, DesignarFuncaoForm, UserCreationProfessor, ProfessorEditForm, \
    RelatorioBimestreForm
from .models import Funcionario, Professor
from ..aluno.models import Aluno
from ..core.models import Usuario
from ..escola.models import UnidadeEscolar, AnoLetivo
from ..frequencia.models import Periodo, Relatorio
from ..funcao.models import Funcao
from ..perfil.models import Endereco, Pessoa
from ..sala.models import Sala

class DashProfessor(LoginRequiredMixin, TemplateView):
    template_name = 'funcionario/professor_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = get_object_or_404(Professor, pk=self.request.user)
        escola = get_object_or_404(UnidadeEscolar, pk=professor.escola.pk)
        ano_corrente = AnoLetivo.objects.get(corrente=True)
        salas = Sala.objects.filter(escola=escola, ano_letivo=ano_corrente).order_by('ano')
        context['escola'] = escola
        context['salas'] = salas
        context['data'] = now()
        return context


class CadastrarProfessor(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Professor
    form_class = UserCreationProfessor
    template_name = 'funcionario/adicionar_professor.html'
    success_message = 'Cadastro Realizado com sucesso!'
    success_url = reverse_lazy('funcionario:lista_professores')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        context['escola'] = escola
        return context

    def form_valid(self, form):
        professor = form.save(commit=False)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        professor.escola = escola
        professor.is_professor = True
        professor.save()
        return super().form_valid(form)


class ListaProfessores(LoginRequiredMixin, ListView):
    model = Professor
    template_name = 'funcionario/lista_professores.html'

    def get_queryset(self):
        return Professor.objects.filter(escola=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escola'] = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        return context


class EditarProfessor(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = ProfessorEditForm
    model = Professor
    success_message = 'Informações do professor atualizadas.'
    template_name = 'funcionario/editar_professor.html'
    success_url = reverse_lazy('funcionario:lista_professores')


class DeletarProfessor(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Professor
    success_message = 'Professor removido com sucesso!'
    success_url = reverse_lazy('funcionario:lista_professores')

    def get_object(self, queryset=None):
        return Professor.objects.get(pk=self.kwargs['pk'])


class ProfAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'funcionario/prof_alunos.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        return Aluno.objects.filter(sala_id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = get_object_or_404(Professor, pk=self.request.user)
        escola = get_object_or_404(UnidadeEscolar, pk=professor.escola.id)
        sala = get_object_or_404(Sala, id=self.kwargs['id'])
        context['escola'] = escola
        context['sala'] = sala
        return context


class ListaAlunosrelatorios(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'funcionario/alunos_relatorios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = get_object_or_404(Sala, pk=self.kwargs['pk'])
        alunos = Aluno.objects.filter(sala=sala).order_by('nome')
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])

        alunos_relatorios = []
        for aluno in alunos:
            aluno_relatorio = []
            aluno_relatorio.append(aluno)
            try:
                periodo = Periodo.objects.get(periodo=self.kwargs['bimestre'])
                relatorio = Relatorio.objects.filter(aluno=aluno, periodo=periodo, data_relatorio__year=datetime.now().year).first()
                aluno_relatorio.append(relatorio)
            except:
                relatorio = None
                aluno_relatorio.append(relatorio)

            alunos_relatorios.append(aluno_relatorio)

        context['bimestre'] = self.kwargs['bimestre']
        context['sala'] = sala
        context['alunos'] = alunos_relatorios
        context['escola'] = escola
        return context