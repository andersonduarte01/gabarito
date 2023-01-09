import calendar
import datetime

from django.urls import reverse_lazy

from .gerarPlanilha import dias_mes, criarFrequencia
from .converter import converter
from django.views.generic import TemplateView, UpdateView

from ..escola.models import UnidadeEscolar
from ..sala.models import Sala
from .models import Frequencia


# Create your views here.

class FreqAtual(TemplateView):
    template_name = 'frequencia/frequencia.html'

    def get_context_data(self, **kwargs):
        context = super(FreqAtual, self).get_context_data(**kwargs)
        resumo = []
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        salas = Sala.objects.filter(escola=escola)
        ano = datetime.date.today().year
        mes = datetime.date.today().month
        mes_atual = dias_mes(mes=mes, ano=ano)
        for sala in salas:
            freq = criarFrequencia(mes_atual, sala)
            resumo.append(freq)
        context['mes'] = mes_atual
        mes01 = converter(mes_atual[0].month)
        context['salas'] = resumo
        context['mes1'] = mes01
        return context


class FreqDiaria(UpdateView):
    model = Frequencia
    fields = ('presentes', 'observacao')
    template_name = 'frequencia/freqdiaria.html'
    success_url = reverse_lazy('frequencia:freq')

    def get_queryset(self):
        return Frequencia.objects.filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(FreqDiaria, self).get_context_data(**kwargs)
        data01 = Frequencia.objects.get(pk=self.kwargs['pk'])
        sala = Sala.objects.get(pk=data01.sala.id)
        context['data'] = data01.data
        context['sala'] = sala
        return context



