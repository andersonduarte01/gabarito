from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView

from .forms import UserCreationFuncionario, DesignarFuncaoForm, UserCreationProfessor, ProfessorEditForm
from .models import Funcionario, Professor
from ..aluno.models import Aluno
from ..core.models import Usuario
from ..escola.models import UnidadeEscolar, AnoLetivo
from ..funcao.models import Funcao
from ..perfil.models import Endereco, Pessoa
from ..sala.models import Sala


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