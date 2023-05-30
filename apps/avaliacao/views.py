from datetime import datetime
from time import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory, RadioSelect
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from .correcao import correcao, alunos_prova
from .forms import RespostaForm, AvaliacaoForm, AvaliacaoUpdateForm, AvaliacaoQuestaoForm, QuestaoForm1, \
    QuestaoFormEditar, AIRespostaForm
from ..aluno.models import Aluno
from ..avaliacao.models import Questao, Avaliacao, Resposta, Gabarito
from ..escola.models import UnidadeEscolar
from ..sala.models import Ano, Sala


class AvaliacaoListEscola(ListView):
    model = Avaliacao
    template_name = 'avaliacao/avaliacoes_escola.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        escola = UnidadeEscolar.objects.get(id=self.request.user.id)
        return escola.avaliacao_escola.all().filter(data_encerramento__gte=datetime.now().date())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escola'] = self.request.user
        return context


class AvaliacaoListSalas(LoginRequiredMixin, ListView):
    model = Sala
    template_name = 'avaliacao/avaliacao_salas.html'
    context_object_name = 'salas'

    def get_queryset(self):
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        avaliacao = Avaliacao.objects.get(id=self.kwargs['id_avaliacao'])
        return Sala.objects.filter(escola=escola, ano=avaliacao.ano)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        avaliacao = Avaliacao.objects.get(id=self.kwargs['id_avaliacao'])
        context['escola'] = escola
        context['avaliacao'] = avaliacao
        return context




class AvaliacaoAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'avaliacao/avaliacao_alunos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avaliacao = Avaliacao.objects.get(pk=self.kwargs['avaliacao_id'])
        sala = Sala.objects.get(pk=self.kwargs['sala_id'])
        alunos = Aluno.objects.filter(sala=self.kwargs['sala_id'])
        escola = get_object_or_404(UnidadeEscolar, slug=sala.escola.slug)
        gabaritos, alunos_avaliar, questoes = alunos_prova(avaliacao=avaliacao, alunos=alunos)
        context['escola'] = escola
        context['avaliacao'] = avaliacao
        context['alunos'] = alunos_avaliar
        context['sala'] = sala
        context['questoes'] = questoes
        context['gabaritos'] = gabaritos
        return context


# # Administrador

def responderProvaAdm(request, aluno_id, avaliacao_id, slug):
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    questoes = Questao.objects.filter(avaliacao=avaliacao)
    QuestaoFormSet = modelformset_factory(Questao, form=AIRespostaForm, extra=0)

    if request.method == 'POST':
        formset = QuestaoFormSet(request.POST, request.FILES, queryset=questoes)
        if formset.is_valid():
            gabarito_resposta = Gabarito.objects.create(avaliacao=avaliacao, aluno=aluno)
            for form in formset:
                opcao_selecionada = form.cleaned_data.get('resposta')
                questao = form.save(commit=False)
                if opcao_selecionada == questao.opcao_certa:
                    resp = Resposta.objects.create(resposta=opcao_selecionada,
                                                   gabarito=gabarito_resposta, questao=questao, acertou=True)
                else:
                    resp = Resposta.objects.create(resposta=opcao_selecionada,
                                                   gabarito=gabarito_resposta, questao=questao)
            gabarito_resposta.concluido = True
            gabarito_resposta.save()
            formset.save()
            url = reverse_lazy('escola:escola_avaliar_alunos',
                               kwargs={'slug': aluno.sala.escola.slug, 'avaliacao_id': avaliacao.id,
                                       'sala_id': aluno.sala.id})
            return HttpResponseRedirect(url)
    else:
        formset = QuestaoFormSet(queryset=questoes)
    return render(request, 'avaliacao/avaliar_aluno_adm.html',
                  {'formset': formset, 'avaliacao': avaliacao, 'aluno': aluno})


def criarAvaliacao(request):
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save()
            url = reverse_lazy('escola:painel_escola')
            return HttpResponseRedirect(url)
    else:
        form = AvaliacaoForm()

    context = {'form': form}
    return render(request, 'avaliacao/adicionar_avaliacao.html', context)


class EditarAvaliacao(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Avaliacao
    form_class = AvaliacaoUpdateForm
    template_name = 'avaliacao/adicionar_avaliacao.html'
    success_message = 'Avaliação atualizada!'
    success_url = reverse_lazy('escola:painel_escola')


class EditarQuestao(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Questao
    fields = ('questao','texto', 'imagem_prova', 'opcao_um', 'opcao_dois', 'opcao_tres', 'opcao_quatro', 'opcao_certa')
    template_name = 'avaliacao/editar_questao.html'
    success_message = 'Questão atualizada!'

    def form_valid(self, form):
        form.save()
        questao = Questao.objects.get(id=self.kwargs['pk'])
        url = reverse_lazy('avaliacao:lista_questoes', kwargs={'pk': questao.avaliacao.id })
        return HttpResponseRedirect(url)


class DeletarQuestao(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Questao
    success_message = 'Questao removida com sucesso!'

    def get_object(self, queryset=None):
        return Questao.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        questao = Questao.objects.get(pk=self.kwargs['pk'])
        return reverse_lazy('avaliacao:lista_questoes', kwargs={'pk': questao.avaliacao.id})


class ListaAvaliacoes(LoginRequiredMixin, ListView):
    model = Avaliacao
    template_name = 'avaliacao/lista_avaliacoes.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        return Avaliacao.objects.all()


class AddQuestao(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Questao
    fields = ('avaliacao', 'texto', 'imagem_prova', 'questao', 'opcao_um', 'opcao_dois', 'opcao_tres', 'opcao_quatro', 'opcao_certa')
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


def iniciarAvaliacao(request, avaliacao_id, aluno_id):
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    questoes = Questao.objects.filter(avaliacao=avaliacao)
    QuestaoFormSet = modelformset_factory(Questao, form=QuestaoForm1, extra=0)

    if request.method == 'POST':
        formset = QuestaoFormSet(request.POST, request.FILES, queryset=questoes)

        if formset.is_valid():
            gabarito_resposta = Gabarito.objects.create(avaliacao=avaliacao, aluno=aluno)
            for form in formset:
                opcao_selecionada = form.cleaned_data.get('opcao')
                questao = form.save(commit=False)
                if opcao_selecionada == questao.opcao_certa:
                    resp = Resposta.objects.create(resposta=opcao_selecionada,
                                                   gabarito=gabarito_resposta, questao=questao, acertou=True)
                else:
                    resp = Resposta.objects.create(resposta=opcao_selecionada,
                                                   gabarito=gabarito_resposta, questao=questao)
            gabarito_resposta.concluido = True
            gabarito_resposta.save()
            formset.save()
            url = reverse_lazy('avaliacao:avaliar_alunos',
                               kwargs={'avaliacao_id': avaliacao.id, 'sala_id': aluno.sala.id})
            return HttpResponseRedirect(url)
    else:
        formset = QuestaoFormSet(queryset=questoes)
    return render(request, 'avaliacao/avaliar_iniciar.html', {'formset': formset, 'avaliacao': avaliacao, 'aluno': aluno})


def RefazerAvaliacao(request, gabarito_id):
    gabarito = get_object_or_404(Gabarito, id=gabarito_id)
    avaliacao = get_object_or_404(Avaliacao, pk=gabarito.avaliacao.id)
    aluno = get_object_or_404(Aluno, pk=gabarito.aluno.id)
    questoes = Questao.objects.filter(avaliacao=avaliacao)
    QuestaoFormSet = modelformset_factory(Questao, form=QuestaoForm1, extra=0)

    if request.method == 'POST':
        formset = QuestaoFormSet(request.POST, request.FILES, queryset=questoes)

        if formset.is_valid():
            gabarito_resposta = get_object_or_404(Gabarito, id=gabarito_id)
            print(formset)
            for form in formset:
                opcao_selecionada = form.cleaned_data.get('opcao')
                questao = form.save(commit=False)
                resp = get_object_or_404(Resposta, questao=questao, gabarito=gabarito)
                if opcao_selecionada == questao.opcao_certa:
                    resp.resposta = opcao_selecionada
                    resp.acertou = True

                else:
                    resp.resposta = opcao_selecionada
                    resp.acertou = False
                resp.save()
            gabarito_resposta.concluido = True
            gabarito_resposta.save()
            formset.save()
            url = reverse_lazy('avaliacao:avaliar_alunos',
                               kwargs={'avaliacao_id': avaliacao.id, 'sala_id': aluno.sala.id})
            return HttpResponseRedirect(url)
    else:
        formset = QuestaoFormSet(queryset=questoes)
    return render(request, 'avaliacao/avaliar_refazer.html', {'formset': formset, 'avaliacao': avaliacao, 'aluno': aluno})


class VerGabarito(LoginRequiredMixin, TemplateView):
    template_name = 'avaliacao/ver_gabarito.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gabarito = Gabarito.objects.get(id=self.kwargs['gabarito_id'])
        respostas = correcao(gabarito=gabarito)
        aluno = Aluno.objects.get(id=gabarito.aluno.id)
        context['respostas'] = respostas
        context['aluno'] = aluno
        context['gabarito'] = gabarito
        return context

