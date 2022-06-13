from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView, TemplateView, CreateView

from ..aluno.models import Aluno
from ..avaliacao.models import Avaliacao
from ..sala.models import Sala


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


class ListarOpcoes(LoginRequiredMixin, TemplateView):
    model = Sala
    template_name = 'sala/opcoes.html'
    context_object_name = 'opcoes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        context['sala'] = sala
        return context


class ListarAlunos(LoginRequiredMixin, CreateView):
    model = Aluno
    fields = ('nome',)
    template_name = 'sala/alunos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        alunos = Aluno.objects.filter(sala=sala).order_by('nome')
        context['sala'] = sala
        context['alunos'] = alunos
        return context

    def form_valid(self, form):
        aluno = form.save(commit=False)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        aluno.sala = sala
        aluno.save()
        return super(ListarAlunos, self).form_valid(form)

    def get_success_url(self):
        return reverse('salas:alunos', kwargs={'pk': self.get_context_data()['sala'].pk})