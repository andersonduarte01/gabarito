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


class AddAluno(LoginRequiredMixin, CreateView):
    form_class = AlunoForm
    template_name = 'aluno/adicionar_aluno.html'
    success_url = reverse_lazy('escola:painel_escola')

    def get_form_kwargs(self):
        kwargs = super(AddAluno, self).get_form_kwargs()
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        kwargs['escola'] = escola
        return kwargs


def editar_aluno(request, pk):
    perfil = ''
    endereco = ''
    aluno = get_object_or_404(Aluno, pk=pk)
    escola = UnidadeEscolar.objects.get(pk=aluno.sala.escola.id)
    try:
        perfil = Pessoa.objects.get(pk=aluno.perfil.id)
        endereco = Endereco.objects.get(pk=aluno.endereco.id)
    except:
        print('Vazio')

    if request.method == 'POST':
        form = EditarAlunoForm(request.POST, instance=aluno)
        form1 = PessoaForm(request.POST, instance=perfil)
        form2 = EnderecoForm(request.POST, instance=endereco)
        if form.is_valid and form1.is_valid() and form2.is_valid():
            aluno = form.save(commit=False)
            perfil = form1.save()
            endereco = form2.save()
            aluno.perfil = perfil
            aluno.endereco = endereco
            aluno.save()
            url = reverse('salas:alunos', kwargs={'pk': aluno.sala.pk})
            return HttpResponseRedirect(url)

    else:
        form = EditarAlunoForm(instance=aluno)
        form1 = PessoaForm(instance=perfil)
        form2 = EnderecoForm(instance=endereco)

    context = {'form': form, 'form1': form1, 'form2': form2, 'escola': escola, 'aluno': aluno, }
    return render(request, "aluno/editar_aluno.html", context)


class EditarAluno(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Aluno
    form_class = EditarAlunoForm01
    template_name = 'aluno/edicao_aluno.html'
    success_message = 'Aluno atualizado com sucesso.'

    def get_success_url(self):
        print(self.object.sala.pk)
        return reverse_lazy('salas:alunos', kwargs={'pk': self.object.sala.pk})

class DeletarAluno(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Aluno
    success_message = 'Aluno removido com sucesso!'

    def get_object(self, queryset=None):
        return Aluno.objects.get(pk=self.kwargs['pk'])


def delete_view(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    sala = get_object_or_404(Sala, id=aluno.sala.id)
    if request.method == "POST":
        aluno.delete()
        sala.total_alunos -= 1
        sala.save()
        url = reverse('salas:alunos', kwargs={'pk': aluno.sala.pk})
        return HttpResponseRedirect(url)

    url = reverse('salas:alunos', kwargs={'pk': aluno.sala.pk})
    return HttpResponseRedirect(url)


class ProvasView(ListView):
    model = Gabarito
    template_name = 'aluno/mostrar.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        return Gabarito.objects.filter(aluno=self.kwargs['pk'])


class ProvaView(ListView):
    model = Resposta
    template_name = 'aluno/prova.html'
    context_object_name = 'respostas'

    def get_queryset(self):
        gabarito = Gabarito.objects.get(pk=self.kwargs['pk'])
        return Resposta.objects.filter(gabarito=gabarito)


class ResultadoPesquisa(ListView):
    model = Aluno
    template_name = 'aluno/resultado.html'

    def get_queryset(self):
        salas = Sala.objects.filter(escola=self.request.user)
        query = self.request.GET.get("q")
        object_list = Aluno.objects.filter(Q(nome__icontains=query), sala__in=salas)
        return object_list


class Pesquisar(TemplateView):
    template_name = 'aluno/pesquisar.html'


class PerfilAluno(ListView):
    model = Aluno
    template_name = 'aluno/perfil_aluno.html'
    context_object_name = 'aluno'

    def get_queryset(self):
        return Aluno.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = Aluno.objects.get(pk=self.kwargs['pk'])
        return context


def relatorioAluno(request, pk, mes):
    sala = get_object_or_404(Sala, pk=pk)
    escola = get_object_or_404(UnidadeEscolar, pk=sala.escola.pk)
    alunos = Aluno.objects.filter(sala=sala).order_by('nome')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{sala.descricao}.pdf"'
    # Dimensões da página e do paralelogramo

    nome_meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',
                  4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho',
                  8: 'Agosto', 9: 'Setembro', 10: 'Outubro',
                  11: 'Novembro', 12: 'Dezembro'
                  }

    c = canvas.Canvas(response, pagesize=landscape(A4))
    ponto1, ponto2, ponto3, ponto4 = desenhar_retangulo(c)
    altura = adicionar_linha_paralela(c, ponto3, ponto4, intervalo=98.65)

    # Nomes cabeçalho
    largura_texto = c.stringWidth(escola.nome_escola, "Helvetica-Bold", 14)  # Obter a largura do texto em pontos

    escrever_texto(c, texto=escola.nome_escola,
                   x=((ponto3[0] - largura_texto) / 2),
                   y=(ponto3[1] - 20), font="Helvetica-Bold", font_size=14,
                   color=(0, 0, 0))

    sala_texto = c.stringWidth(sala.descricao, "Helvetica", 14)

    escrever_texto(c, texto=sala.descricao,
                   x=((ponto3[0] - sala_texto) / 2),
                   y=(ponto3[1] - 40), font="Helvetica", font_size=14,
                   color=(0, 0, 0))

    ano_texto = c.stringWidth(f'{sala.ano} - {sala.turno}', "Helvetica", 14)

    escrever_texto(c, texto=f'{sala.ano} - {sala.turno}',
                   x=((ponto3[0] - ano_texto) / 2),
                   y=(ponto3[1] - 60), font="Helvetica", font_size=14,
                   color=(0, 0, 0))

    mes_texto = c.stringWidth(f'{nome_meses[mes]} - 2024', "Helvetica", 14)


    escrever_texto(c, texto=f'{nome_meses[mes]} - 2024',
                   x=((ponto3[0] - mes_texto) / 2),
                   y=(ponto3[1] - 85), font="Helvetica", font_size=14,
                   color=(0, 0, 0))

    altura1 = adicionar_linha_paralela(c, ponto3, ponto4, intervalo=118.65)

    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

    ano = 2024
    dias_mes = calendar.monthcalendar(ano, mes)
    resultado = []  # Cabeçalho da tabela
    resultado1 = ['']  # Cabeçalho da tabela
    resultado2 = ['Alunos']  # Cabeçalho da tabela
    resultado_conferir = []  # Cabeçalho da tabela
    alunos_tag = []

    # Percorre as semanas do mês
    for semana in dias_mes:
        for dia in semana:
            if dia != 0:  # Ignora os dias vazios no início ou fim do mês
                data = datetime(ano, mes, dia)
                if data.weekday() < 5:
                    resultado2.append(data.strftime('%d'))
                    resultado1.append(data.strftime('%a'))
                    resultado_conferir.append(data.strftime('%Y-%m-%d'))

    resultado.append(resultado2)
    resultado.append(resultado1)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),  # Cor de fundo para o cabeçalho
        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # Cor do texto para o cabeçalho
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alinhamento central para todas as células
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
        ('GRID', (0, 0), (-1, -1), 1, (0.8, 0.8, 0.8)),
    ])


    for aluno in alunos:
        alunos_tag = []
        alunos_tag.append(aluno.nome)
        contador = 0
        for semana in dias_mes:
            for dia in semana:
                if dia != 0:  # Ignora os dias vazios no início ou fim do mês
                    data = datetime(ano, mes, dia)
                    if data.weekday() < 5:
                        try:
                            frequencia = FrequenciaAluno.objects.get(data=data.date(), aluno=aluno)
                            if frequencia.presente:
                                alunos_tag.append('P')
                            else:
                                alunos_tag.append('F')

                        except:
                            alunos_tag.append('.')
            contador += 1
            print(contador)

        resultado.append(alunos_tag)


    largura_disponivel = (27 * 28.35)
    percorrer = largura_disponivel
    larguras_colunas = [188.95]

    while(percorrer > 1):
        larguras_colunas.append(25)
        percorrer -= 25

    t = Table(resultado, colWidths=larguras_colunas)
    largura_tabela, altura_tabela = t.wrapOn(None, largura_disponivel, 0)
    t.setStyle(style)
    largura_tabela = 27 * 28.35
    posicao_horizontal_tabela = ponto4[0]
    t.wrapOn(c, largura_tabela, 100)
    t.drawOn(c, ponto1[0] + (((27 * 28.35) - largura_tabela) / 2), altura1)

    c.save()
    return response
