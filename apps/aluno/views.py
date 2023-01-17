from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, TemplateView, DetailView, ListView, CreateView

from ..aluno.models import Aluno
from ..avaliacao.models import Gabarito, Resposta
from .forms import AlunoForm
from ..escola.models import UnidadeEscolar
from ..sala.models import Sala


class AddAluno(LoginRequiredMixin, CreateView):
    form_class = AlunoForm
    template_name = 'aluno/adicionar_aluno.html'
    success_url = reverse_lazy('escola:painel_escola')

    def get_form_kwargs(self):
        kwargs = super(AddAluno, self).get_form_kwargs()
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        kwargs['escola'] = escola
        return kwargs


class EditarAluno(LoginRequiredMixin, UpdateView):
    model = Aluno
    fields = ('nome',)
    template_name = 'aluno/editar_aluno.html'

    def get_success_url(self):
        return reverse('salas:alunos', kwargs={'pk': self.get_context_data()['aluno'].sala.pk})


class DeletarAluno(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Aluno
    success_message = 'Aluno removido com sucesso!'

    def get_object(self, queryset=None):
        return Aluno.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('salas:alunos', kwargs={'pk': self.get_context_data()['aluno'].sala.pk})


class ProvasView(ListView):
    model = Gabarito
    template_name = 'aluno/mostrar.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        return Gabarito.objects.filter(aluno=self.kwargs['pk'])


class ProvaView(ListView):
    model = Resposta
    template_name = 'aluno/prova.html'
    context_object_name = 'respostas'

    def get_queryset(self):
        gabarito = Gabarito.objects.get(pk=self.kwargs['pk'])
        return Resposta.objects.filter(gabarito=gabarito)
