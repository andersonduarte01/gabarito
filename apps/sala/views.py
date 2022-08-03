from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView

from ..aluno.models import Aluno
from ..avaliacao.models import Avaliacao
from ..escola.models import UnidadeEscolar
from ..sala.models import Sala, Ano


class AdicionarAno(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ano
    fields = ('descricao',)
    template_name = 'sala/adicionar_ano.html'
    success_message = 'Ano cadastrado com sucesso.'
    success_url = reverse_lazy('escola:painel_escola')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class AdicionarSala(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Sala
    fields = ('descricao', 'turno', 'ano')
    template_name = 'sala/adicionar_sala.html'
    success_message = 'Sala cadastrada com sucesso.'
    success_url = reverse_lazy('escola:painel_escola')

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


class ListaAvaliacoesAdm(LoginRequiredMixin, ListView):
    model = Avaliacao
    template_name = 'sala/avaliacoes_adm.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        return Avaliacao.objects.filter(ano=sala.ano)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        escola = UnidadeEscolar.objects.get(slug=self.kwargs['slug'])
        context['sala'] = sala
        context['escola'] = escola
        return context


class ListarOpcoes(LoginRequiredMixin, TemplateView):
    model = Sala
    template_name = 'sala/opcoes.html'
    context_object_name = 'opcoes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        escola = UnidadeEscolar.objects.get(pk=sala.escola.pk)
        context['sala'] = sala
        context['escola'] = escola
        return context


class ListarAlunos(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Aluno
    fields = ('nome',)
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
        aluno.sala = sala
        aluno.save()
        return super(ListarAlunos, self).form_valid(form)

    def get_success_url(self):
        return reverse('salas:alunos', kwargs={'pk': self.get_context_data()['sala'].pk})