from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

from .correcao import criarGabaritos, alinharquestoes, correcao
from .forms import RespostaForm
from ..aluno.models import Aluno
from ..avaliacao.models import Questao, Avaliacao, Resposta, Gabarito
from ..escola.models import UnidadeEscolar
from ..sala.models import Ano, Sala


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


def responderProva1(request, sala_id, avaliacao_id):
        sala = Sala.objects.get(pk=sala_id)
        avaliacao = Avaliacao.objects.get(pk=avaliacao_id)
        aluno = Aluno.objects.filter(sala=sala).first()
        gabarito = Gabarito.objects.get(aluno=aluno, avaliacao=avaliacao)
        respostas = Resposta.objects.filter(gabarito=gabarito)
        RespostasFormSet = modelformset_factory(Resposta, fields=('resposta',), extra=0)

        if request.method == 'POST':
            formset = RespostasFormSet(request.POST, request.FILES, queryset=respostas,)
            if formset.is_valid():
                formset.save()
            return HttpResponseRedirect(reverse('escola:painel_escola'))
        else:
            formset = RespostasFormSet(queryset=respostas)
        return render(request, 'avaliacao/resposta.html', {'formset':formset})


class AvaliacaoAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'avaliacao/avaliacao_alunos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avaliacao = Avaliacao.objects.get(pk=self.kwargs['avaliacao_id'])
        sala = Sala.objects.get(pk=self.kwargs['sala_id'])
        criarGabaritos(avaliacao=avaliacao, sala=sala)
        alinharquestoes(avaliacao, sala)
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

# Administrador

class AvaliacaoAlunosAdm(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'avaliacao/avaliacao_alunos_adm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avaliacao = Avaliacao.objects.get(pk=self.kwargs['avaliacao_id'])
        sala = Sala.objects.get(pk=self.kwargs['sala_id'])
        criarGabaritos(avaliacao=avaliacao, sala=sala)
        alinharquestoes(avaliacao, sala)
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
