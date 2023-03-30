import datetime

from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy
from .gerarPlanilha import criarFrequenciaDiaria
from django.views.generic import UpdateView
from datetime import datetime
from.forms import FrequenciaAlunoForm

from ..aluno.models import Aluno
from .gerarPlanilha import percentual
from ..escola.models import UnidadeEscolar
from ..sala.models import Sala
from .models import Frequencia, FrequenciaAluno


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


def frequencia_diaria(request, cal, sala_id):
    x = cal.replace("-", "/")
    data = datetime.strptime(x, '%Y/%m/%d')
    sala = Sala.objects.get(pk=sala_id)
    escola = UnidadeEscolar.objects.get(pk=sala.escola.pk)
    alunos = Aluno.objects.filter(sala=sala)
    criarFrequenciaDiaria(alunos=alunos, data=data)
    frequencias = FrequenciaAluno.objects.filter(data=data, aluno__in=alunos).order_by()
    RespostasFormSet = modelformset_factory(FrequenciaAluno, form=FrequenciaAlunoForm, extra=0)

    if request.method == 'POST':
        formset = RespostasFormSet(request.POST, request.FILES, queryset=frequencias,)
        if formset.is_valid():
            formset.save()
            url = reverse_lazy('escola:painel_planilha_00', kwargs={'slug': escola.slug, 'data': data.date()})
            return HttpResponseRedirect(url)
    else:
        formset = RespostasFormSet(queryset=frequencias)
    return render(request, 'frequencia/frequencia_aluno.html',
                  {'formset': formset, 'escola': escola, 'sala': sala, 'data': data.date()})
