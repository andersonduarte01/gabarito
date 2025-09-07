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
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer

from .relatorio import desenhar_retangulo, adicionar_linha_paralela, adicionar_linha_vertical, escrever_texto, \
    desenhar_retangulo1
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


def relatorioFrequencia(request, pk, mes):
    sala = get_object_or_404(Sala, pk=pk)
    escola = get_object_or_404(UnidadeEscolar, pk=sala.escola.pk)
    alunos = Aluno.objects.filter(sala=sala).order_by("nome")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{sala.descricao}.pdf"'

    # Documento em modo paisagem
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Cabeçalho
    elements.append(Paragraph(f"<b>{escola.nome_escola}</b>", styles["Title"]))
    elements.append(Paragraph(f"{sala.descricao}", styles["Heading2"]))
    elements.append(Paragraph(f"{sala.ano} - {sala.turno}", styles["Normal"]))

    nome_meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    elements.append(Paragraph(f"{nome_meses[mes]} - 2025", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Preparar tabela
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    ano = 2025
    dias_mes = calendar.monthcalendar(ano, mes)

    header_dias = ["Alunos"]
    header_semana = [""]

    for semana in dias_mes:
        for dia in semana:
            if dia != 0:
                data = datetime(ano, mes, dia)
                if data.weekday() < 5:  # dias úteis
                    header_dias.append(data.strftime("%d"))
                    header_semana.append(data.strftime("%a"))

    data_table = [header_dias, header_semana]

    for aluno in alunos:
        linha = [aluno.nome]
        for semana in dias_mes:
            for dia in semana:
                if dia != 0:
                    data = datetime(ano, mes, dia)
                    if data.weekday() < 5:
                        try:
                            freq = FrequenciaAluno.objects.get(data=data.date(), aluno=aluno)
                            linha.append("P" if freq.presente else "F")
                        except:
                            linha.append(".")
        data_table.append(linha)

    # Largura dinâmica das colunas (paisagem A4)
    total_width = 29.7*cm - 2*cm  # largura útil (paisagem menos margens)
    nome_col_width = 6*cm
    restantes = len(header_dias) - 1
    col_widths = [nome_col_width] + [(total_width - nome_col_width) / restantes] * restantes

    # Criar tabela
    table = Table(data_table, colWidths=col_widths, repeatRows=2)

    # Estilos
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (-1, 1), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ])

    # Zebra striping
    for row_num in range(2, len(data_table)):
        bg_color = colors.whitesmoke if row_num % 2 == 0 else colors.white
        style.add('BACKGROUND', (0, row_num), (-1, row_num), bg_color)

    table.setStyle(style)
    elements.append(table)

    doc.build(elements)
    return response


def relatorioRegistro(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    escola = get_object_or_404(UnidadeEscolar, pk=aluno.sala.escola.pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{aluno}.pdf"'
    # Dimensões da página e do paralelogramo


    c = canvas.Canvas(response, pagesize=A4)
    ponto1, ponto2, ponto3, ponto4 = desenhar_retangulo1(c)
    altura = adicionar_linha_paralela(c, ponto3, ponto4, intervalo=98.65)


    escrever_texto(c, texto=aluno.nome,
                   x=(ponto1[0] + 5),
                   y=(ponto3[1] - 20), font="Helvetica-Bold", font_size=14,
                   color=(0, 0, 0))


    escrever_texto(c, texto=aluno.sala.escola.nome_escola,
                   x=(ponto1[0] + 5),
                   y=(ponto3[1] - 40), font="Helvetica", font_size=12,
                   color=(0, 0, 0))

    escrever_texto(c, texto=aluno.sala.descricao,
                   x=(ponto1[0] + 5),
                   y=(ponto3[1] - 60), font="Helvetica", font_size=12,
                   color=(0, 0, 0))

    escrever_texto(c, texto=aluno.sala.turno,
                   x=(ponto1[0] + 5),
                   y=(ponto3[1] - 80), font="Helvetica", font_size=12,
                   color=(0, 0, 0))


    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),  # Cor de fundo para o cabeçalho
        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # Cor do texto para o cabeçalho
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alinhamento central para todas as células
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
        ('GRID', (0, 0), (-1, -1), 1, (0.8, 0.8, 0.8)),
    ])


    c.save()
    return response
