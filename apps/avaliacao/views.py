from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, CreateView, FormView, UpdateView

from .correcao import criarGabarito, alinharquestoes
from .forms import RespostaForm
from ..aluno.models import Aluno
from ..avaliacao.models import Questao, Avaliacao, Resposta, Gabarito
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


# class RespostaView(CreateView):
#     model = Resposta
#     fields = ('resposta',)
#     template_name = 'avaliacao/resposta.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#
#     def form_valid(self, form):
#         resposta = form.save(commit=False)
#         gabarito = Gabarito.objects.get(pk=11)
#         questao = Questao.objects.get(pk=5)
#         resposta.gabarito = gabarito
#         resposta.questao = questao
#         resposta.save()
#         return super(RespostaView, self).form_valid(form)


# def parametrosGabarito(request, avaliacao_id, sala_id):
#     sala = Sala.objects.get(pk=sala_id)
#     avaliacao = Avaliacao.objects.get(pk=avaliacao_id)
#     criarGabarito(sala=sala, avaliacao=avaliacao)
#     alinharquestoes(sala=sala, avaliacao=avaliacao)
#     return render(request, 'sala/teste.html')

# class ProvaUpdate(UpdateView):
#     model = Resposta
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['avaliacao'] = self.avaliacao_id
#         kwargs['sala'] = self.sala_id
#         return kwargs

def responderProva(request, sala_id, avaliacao_id):
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
