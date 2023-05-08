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

from .correcao import criarGabaritos, alinharquestoes, correcao
from .forms import RespostaForm, AvaliacaoForm, AvaliacaoUpdateForm, AvaliacaoQuestaoForm, QuestaoForm1, \
    QuestaoFormEditar
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



# class AvaliacaoView(ListView):
#     model = Questao
#     template_name = 'avaliacao/avaliacao.html'
#
#     def get_queryset(self):
#         return Questao.objects.filter(avaliacao=self.kwargs['pk'])
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         avaliacao = Avaliacao.objects.get(pk=self.kwargs['pk'])
#         sala = Sala.objects.get(pk=self.kwargs['sala_id'])
#         ano = Ano.objects.get(id=avaliacao.ano.id)
#         context['avaliacao'] = avaliacao
#         context['ano'] = ano
#         context['sala'] = sala
#         return context
#

class AvaliacaoAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'avaliacao/avaliacao_alunos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avaliacao = Avaliacao.objects.get(pk=self.kwargs['avaliacao_id'])
        sala = Sala.objects.get(pk=self.kwargs['sala_id'])
        alunos = Aluno.objects.filter(sala=self.kwargs['sala_id'])
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['avaliacao'] = avaliacao
        context['alunos'] = alunos
        context['sala'] = sala
        return context

#
# def responderProvaAluno(request, aluno_id, avaliacao_id):
#     aluno = Aluno.objects.get(pk=aluno_id)
#     avaliacao = Avaliacao.objects.get(pk=avaliacao_id)
#     questoes = Questao.objects.filter(avaliacao=avaliacao)
#     QuestoesFormSet = modelformset_factory(Questao, form=AvaliacaoQuestaoForm, extra=0)
#
#     if request.method == 'POST':
#         formset = QuestoesFormSet(request.POST, request.FILES, queryset=questoes)
#         if formset.is_valid():
#             formset.save()
#         return HttpResponseRedirect(reverse('escola:painel_escola'))
#     else:
#         formset = QuestoesFormSet(queryset=questoes)
#     return render(request, 'avaliacao/avaliar_iniciar.html', {'questoes': questoes, 'avaliacao': avaliacao, 'aluno': aluno})
#
# # Administrador
#
#
# class AvaliacaoAlunosAdm(LoginRequiredMixin, ListView):
#     model = Aluno
#     template_name = 'avaliacao/avaliacao_alunos_adm.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         avaliacao = Avaliacao.objects.get(pk=self.kwargs['avaliacao_id'])
#         sala = Sala.objects.get(pk=self.kwargs['sala_id'])
#         #criarGabaritos(avaliacao=avaliacao, sala=sala)
#         #alinharquestoes(avaliacao, sala)
#         alunos = Aluno.objects.filter(sala=self.kwargs['sala_id'])
#         escola = UnidadeEscolar.objects.get(slug=self.kwargs['slug'])
#         context['escola'] = escola
#         context['avaliacao'] = avaliacao
#         context['alunos'] = alunos
#         context['sala'] = sala
#         return context
#
#
# def responderProvaAdm(request, aluno_id, avaliacao_id, slug):
#     escola = UnidadeEscolar.objects.get(slug=slug)
#     aluno = Aluno.objects.get(pk=aluno_id)
#     sala = Sala.objects.get(pk=aluno.sala.pk)
#     avaliacao = Avaliacao.objects.get(pk=avaliacao_id)
#     gabarito = Gabarito.objects.get(aluno=aluno, avaliacao=avaliacao)
#     respostas = Resposta.objects.filter(gabarito=gabarito)
#     RespostasFormSet = modelformset_factory(Resposta, form=RespostaForm, extra=0)
#
#     if request.method == 'POST':
#         formset = RespostasFormSet(request.POST, request.FILES, queryset=respostas,)
#         if formset.is_valid():
#             formset.save()
#             correcao(gabarito)
#             gabarito.concluido = True
#             gabarito.save()
#             url = reverse('avaliacao:avaliar_adm', kwargs={'slug': escola.slug,
#                                                            'avaliacao_id': avaliacao.id, 'sala_id': sala.id })
#         return HttpResponseRedirect(url)
#
#     else:
#         formset = RespostasFormSet(queryset=respostas)
#         correcao(gabarito)
#     return render(request, 'avaliacao/avaliar_aluno_adm.html',
#                   {'formset': formset, 'avaliacao': avaliacao, 'escola': escola, 'sala': sala, 'aluno': aluno})
#
#
# # class AddAvaliacao(LoginRequiredMixin, SuccessMessageMixin, CreateView):
# #     model = Avaliacao
# #     fields = ('descricao', 'ano')
# #     template_name = 'avaliacao/adicionar_avaliacao.html'
# #     success_message = 'Avaliação cadastrada com sucesso.'
# #     success_url = reverse_lazy('escola:painel_escola')
#
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
    fields = ('questao', 'opcao_um', 'opcao_dois', 'opcao_tres', 'opcao_quatro', 'opcao_certa')
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

#
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


def iniciarAvaliacao(request, avaliacao_id, aluno_id):
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    aluno = get_object_or_404(Aluno, pk=aluno_id)

    try:
        gabarito = Gabarito.objects.get(avaliacao=avaliacao, aluno=aluno)
        return HttpResponseRedirect(reverse_lazy('avaliacao:ver_gabarito', kwargs={'gabarito_id': gabarito.id}))
    except:
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
                return HttpResponseRedirect(reverse('core:inicio'))
        else:
            formset = QuestaoFormSet(queryset=questoes)
        return render(request, 'avaliacao/avaliar_iniciar.html', {'formset': formset, 'avaliacao': avaliacao, 'aluno': aluno})


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




# def EditarAvaliacao(request, avaliacao_id, aluno_id):
#     aluno = Aluno.objects.get(pk=aluno_id)
#     avaliacao = Avaliacao.objects.get(pk=avaliacao_id)
#     gabarito = get_object_or_404(Gabarito, avaliacao=avaliacao, aluno=aluno)
#     respostas = get_list_or_404(Resposta, gabarito=gabarito)
#     questoes = []
#     for r in respostas:
#         q = get_object_or_404(Questao, id=r.questao.id)
#         questoes.append(q)
#     QuestoesFormSet = modelformset_factory(Questao, form=AvaliacaoQuestaoForm, extra=0)
#
#     if request.method == 'POST':
#         formset = QuestoesFormSet(request.POST, request.FILES, queryset=questoes)
#         if formset.is_valid():
#             formset.save()
#         return HttpResponseRedirect(reverse('escola:painel_escola'))
#     else:
#         formset = QuestoesFormSet(queryset=questoes)
#     return render(request, 'avaliacao/avaliar_iniciar.html', {'questoes': questoes, 'avaliacao': avaliacao, 'aluno': aluno})
