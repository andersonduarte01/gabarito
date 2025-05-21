import locale
from io import BytesIO
import calendar
from datetime import datetime
import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, ListView, CreateView, TemplateView, UpdateView
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from .relatorio import desenhar_retangulo, adicionar_linha_paralela, adicionar_linha_vertical, escrever_texto
from ..aluno.models import Aluno
from ..avaliacao.models import Gabarito, Resposta
from .forms import AlunoForm, EditarAlunoForm, PessoaForm, EnderecoForm, EditarAlunoForm01
from ..escola.models import UnidadeEscolar
from ..frequencia.models import FrequenciaAluno
from ..perfil.models import Pessoa, Endereco
from ..sala.models import Sala


class EditarAluno(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Aluno
    form_class = EditarAlunoForm01
    template_name = 'aluno/edicao_aluno.html'
    success_message = 'Aluno atualizado com sucesso.'

    def get_success_url(self):
        print(self.object.sala.pk)
        return reverse_lazy('escola:unidade_sala_alunos', kwargs={'id': self.object.sala.id,
                                                                  'slug': self.object.sala.escola.slug})

def delete_view(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    sala = get_object_or_404(Sala, id=aluno.sala.id)
    if request.method == "POST":
        aluno.delete()
        sala.total_alunos -= 1
        sala.save()
        url = reverse('escola:unidade_sala_alunos', kwargs={'id': aluno.sala.id,
                                                            'slug': aluno.sala.escola.slug})
        return HttpResponseRedirect(url)

    url = reverse('escola:unidade_sala_alunos', kwargs={'id': aluno.sala.id,
                                                            'slug': aluno.sala.escola.slug})
    return HttpResponseRedirect(url)
