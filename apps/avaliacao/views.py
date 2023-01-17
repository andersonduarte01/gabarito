from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView

from .correcao import criarGabaritos, alinharquestoes, correcao
from .forms import RespostaForm, AvaliacaoForm
from ..aluno.models import Aluno
from ..avaliacao.models import Questao, Avaliacao, Resposta, Gabarito
from ..escola.models import UnidadeEscolar
from ..sala.models import Ano, Sala


class AvaliacaoList(ListView):
    model = Avaliacao
    template_name = 'avaliacao/avaliacoes_aluno.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        return Avaliacao.objects.filter(ano=sala.ano)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        aluno = Aluno.objects.get(pk=self.kwargs['id'])
        context['escola'] = self.request.user
        context['sala'] = sala
        context['aluno'] = aluno
        return context


class AvaliacaoView(ListView):
    model = Questao
    template_name = 'avaliacao/avaliacao.html'

    def get_queryset(self):
        return Questao.objects.filter(avaliacao=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avaliacao = Avaliacao.objects.get(pk=self.kwargs['pk'])
        sala = Sala.objects.get(pk=self.kwargs['sala_id'])
        ano = Ano.objects.get(id=avaliacao.ano.id)
        context['avaliacao'] = avaliacao
        context['ano'] = ano
        context['sala'] = sala
        return context


class AvaliacaoAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'avaliacao/avaliacao_alunos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avaliacao = Avaliacao.objects.get(pk=self.kwargs['avaliacao_id'])
        sala = Sala.objects.get(pk=self.kwargs['sala_id'])
        #criarGabaritos(avaliacao=avaliacao, sala=sala)
        #alinharquestoes(avaliacao, sala)
        alunos = Aluno.objects.filter(sala=self.kwargs['sala_id'])
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['avaliacao'] = avaliacao
        context['alunos'] = alunos
        context['sala'] = sala
        return context


def responderProva(request, aluno_id, avaliacao_id):
    aluno = Aluno.objects.get(pk=aluno_id)
    avaliacao = Avaliacao.objects.get(pk=avaliacao_id)
    gabarito = Gabarito.objects.get(aluno=aluno, avaliacao=avaliacao)
    respostas = Resposta.objects.filter(gabarito=gabarito)
    RespostasFormSet = modelformset_factory(Resposta, form=RespostaForm, extra=0)

    if request.method == 'POST':
        formset = RespostasFormSet(request.POST, request.FILES, queryset=respostas,)
        if formset.is_valid():
            formset.save()
            print('correção')
            correcao(gabarito)
            print('corrigido')
        return HttpResponseRedirect(reverse('escola:painel_escola'))
    else:
        formset = RespostasFormSet(queryset=respostas)
        correcao(gabarito)
    return render(request, 'avaliacao/avaliar_aluno.html', {'formset': formset, 'avaliacao': avaliacao})


def responderProvaAluno(request, aluno_id, avaliacao_id):
    aluno = Aluno.objects.get(pk=aluno_id)
    avaliacao = Avaliacao.objects.get(pk=avaliacao_id)
    questoes = Questao.objects.filter(avaliacao=avaliacao)
    QuestoesFormSet = modelformset_factory(Questao, form=AvaliacaoForm, extra=0)

    if request.method == 'POST':
        formset = QuestoesFormSet(request.POST, request.FILES, queryset=questoes)
        if formset.is_valid():
            formset.save()
        return HttpResponseRedirect(reverse('escola:painel_escola'))
    else:
        formset = QuestoesFormSet(queryset=questoes)
    return render(request, 'avaliacao/avaliar_iniciar.html', {'questoes': questoes, 'avaliacao': avaliacao, 'aluno': aluno})

# Administrador


class AvaliacaoAlunosAdm(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'avaliacao/avaliacao_alunos_adm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avaliacao = Avaliacao.objects.get(pk=self.kwargs['avaliacao_id'])
        sala = Sala.objects.get(pk=self.kwargs['sala_id'])
        #criarGabaritos(avaliacao=avaliacao, sala=sala)
        #alinharquestoes(avaliacao, sala)
        alunos = Aluno.objects.filter(sala=self.kwargs['sala_id'])
        escola = UnidadeEscolar.objects.get(slug=self.kwargs['slug'])
        context['escola'] = escola
        context['avaliacao'] = avaliacao
        context['alunos'] = alunos
        context['sala'] = sala
        return context


def responderProvaAdm(request, aluno_id, avaliacao_id, slug):
    escola = UnidadeEscolar.objects.get(slug=slug)
    aluno = Aluno.objects.get(pk=aluno_id)
    sala = Sala.objects.get(pk=aluno.sala.pk)
    avaliacao = Avaliacao.objects.get(pk=avaliacao_id)
    gabarito = Gabarito.objects.get(aluno=aluno, avaliacao=avaliacao)
    respostas = Resposta.objects.filter(gabarito=gabarito)
    RespostasFormSet = modelformset_factory(Resposta, form=RespostaForm, extra=0)

    if request.method == 'POST':
        formset = RespostasFormSet(request.POST, request.FILES, queryset=respostas,)
        if formset.is_valid():
            formset.save()
            correcao(gabarito)
            gabarito.concluido = True
            gabarito.save()
            url = reverse('avaliacao:avaliar_adm', kwargs={'slug': escola.slug,
                                                           'avaliacao_id': avaliacao.id, 'sala_id': sala.id })
        return HttpResponseRedirect(url)

    else:
        formset = RespostasFormSet(queryset=respostas)
        correcao(gabarito)
    return render(request, 'avaliacao/avaliar_aluno_adm.html',
                  {'formset': formset, 'avaliacao': avaliacao, 'escola': escola, 'sala': sala, 'aluno': aluno})


class AddAvaliacao(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Avaliacao
    fields = ('descricao', 'ano')
    template_name = 'avaliacao/adicionar_avaliacao.html'
    success_message = 'Avaliação cadastrada com sucesso.'
    success_url = reverse_lazy('escola:painel_escola')


class ListaAvaliacoes(LoginRequiredMixin, ListView):
    model = Avaliacao
    template_name = 'avaliacao/lista_avaliacoes.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        return Avaliacao.objects.all()


class AddQuestao(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Questao
    fields = ('avaliacao', 'questao', 'opcao_um', 'opcao_dois', 'opcao_tres', 'opcao_quatro', 'opcao_certa')
    template_name = 'avaliacao/adicionar_questao.html'
    success_message = 'questão cadastrada com sucesso.'
    success_url = reverse_lazy('escola:painel_escola')


class ListaQuestoes(LoginRequiredMixin, ListView):
    model = Questao
    template_name = 'avaliacao/lista_questoes.html'
    context_object_name = 'questoes'

    def get_queryset(self):
        avaliacao = Avaliacao.objects.get(pk=self.kwargs['pk'])
        return Questao.objects.filter(avaliacao=avaliacao)