from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from ..aluno.models import Aluno
from ..avaliacao.models import Avaliacao
from ..escola.models import UnidadeEscolar
from ..funcionario.models import Professor
from ..sala.models import Sala


class AdicionarSala(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Sala
    fields = ('descricao', 'turno', 'ano')
    template_name = 'sala/adicionar_sala.html'
    success_message = 'Sala cadastrada com sucesso.'
    success_url = reverse_lazy('salas:salas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context

    def form_valid(self, form):
        sala = form.save(commit=False)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        sala.escola = escola
        sala.save()
        return super().form_valid(form)


class ListaSalas(LoginRequiredMixin, ListView):
    model = Sala
    template_name = 'sala/salas.html'
    context_object_name = 'salas'

    def get_queryset(self):
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        return Sala.objects.filter(escola=escola).order_by('ano')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class ListaAvaliacoes(LoginRequiredMixin, ListView):
    model = Avaliacao
    template_name = 'sala/salas_avaliacao.html'
    context_object_name = 'salas'

    def get_queryset(self):
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        return Sala.objects.filter(escola=escola).order_by('ano')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class EditarSala(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Sala
    fields = ('descricao', 'turno', 'ano')
    success_message = 'Sala atualizada com sucesso.'
    template_name = 'sala/editar_sala.html'

    def get_success_url(self):
        return reverse('salas:salas')


class DeletarSala(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Sala
    success_message = 'sala removida com sucesso!'

    def get_object(self, queryset=None):
        return Sala.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('salas:salas')


class ListaAvaliacoes(LoginRequiredMixin, ListView):
    model = Avaliacao
    template_name = 'sala/avaliacoes.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        return Avaliacao.objects.filter(ano=sala.ano)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        context['sala'] = sala
        return context
#
#
# class ListaAvaliacoesAdm(LoginRequiredMixin, ListView):
#     model = Avaliacao
#     template_name = 'sala/avaliacoes_adm.html'
#     context_object_name = 'avaliacoes'
#
#     def get_queryset(self):
#         sala = Sala.objects.get(pk=self.kwargs['pk'])
#         return Avaliacao.objects.filter(ano=sala.ano)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         sala = Sala.objects.get(pk=self.kwargs['pk'])
#         escola = UnidadeEscolar.objects.get(slug=self.kwargs['slug'])
#         context['sala'] = sala
#         context['escola'] = escola
#         return context
#


class ListarAlunos(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Aluno
    fields = ('nome', 'data_nascimento', 'sexo')
    success_message = 'Aluno cadastrado com sucesso.'
    template_name = 'sala/alunos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        alunos = Aluno.objects.filter(sala=sala).order_by('nome')
        escola = UnidadeEscolar.objects.get(pk=sala.escola.pk)
        context['sala'] = sala
        context['alunos'] = alunos
        context['escola'] = escola
        return context

    def form_valid(self, form):
        aluno = form.save(commit=False)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        sala.total_alunos += 1
        sala.save()
        aluno.sala = sala
        aluno.save()
        return super(ListarAlunos, self).form_valid(form)

    def get_success_url(self):
        return reverse('salas:alunos', kwargs={'pk': self.get_context_data()['sala'].pk})


class ListarAlunosProfessor(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'sala/alunos_professor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        alunos = Aluno.objects.filter(sala=sala).order_by('nome')
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        context['sala'] = sala
        context['alunos'] = alunos
        context['escola'] = escola
        context['professor'] = professor
        return context


class AlunosAvaliacao(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'sala/alunos_avaliacao.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        return Aluno.objects.filter(sala=self.kwargs['pk']).order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        context['sala'] = sala
        context['escola'] = escola
        return context


class ListaSalasProf(LoginRequiredMixin, ListView):
    model = Sala
    template_name = 'sala/salas-prof.html'
    context_object_name = 'salas'

    def get_queryset(self):
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        return Sala.objects.filter(escola=escola).order_by('ano')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        context['escola'] = escola
        context['professor'] = professor
        return context