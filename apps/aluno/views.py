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
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, PageBreak
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .relatorio import desenhar_retangulo, adicionar_linha_paralela, adicionar_linha_vertical, escrever_texto, \
    desenhar_retangulo1
from ..aluno.models import Aluno
from ..avaliacao.models import Gabarito, Resposta
from .forms import AlunoForm, EditarAlunoForm, PessoaForm, EnderecoForm, EditarAlunoForm01
from ..escola.models import UnidadeEscolar
from ..frequencia.models import FrequenciaAluno, Relatorio
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


def relatorioFrequencia(request, pk, mes, styles=None):
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

    centered_heading = ParagraphStyle(
        name="CenteredHeading2",
        fontSize=14,
        leading=18,
        alignment=TA_CENTER
    )

    centered_heading1 = ParagraphStyle(
        name="CenteredHeading2",
        fontSize=12,
        leading=18,
        alignment=TA_CENTER
    )

    elements = []
    styles = getSampleStyleSheet()

    # Cabeçalho
    elements.append(Paragraph(f"<b>{escola.nome_escola}</b>", styles["Title"]))
    elements.append(Paragraph(f"{sala.descricao} - {sala.ano}", centered_heading))

    nome_meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    elements.append(Paragraph(f"<b>{nome_meses[mes]} - {sala.ano_letivo.ano}</b>",centered_heading1))
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

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="relatorios_{aluno.nome}.pdf"'

    # Documento no formato retrato
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    centered_heading = ParagraphStyle(
        name="CenteredHeading2",
        fontSize=14,
        leading=18,
        alignment=TA_CENTER
    )

    centered_heading1 = ParagraphStyle(
        name="CenteredHeading2",
        fontSize=10,
        leading=18,
        alignment=TA_CENTER
    )

    elements = []
    styles = getSampleStyleSheet()

    # Cabeçalho do aluno
    elements.append(Paragraph(f"<b>{aluno.nome}</b>", styles["Title"]))
    elements.append(Paragraph(f"{escola.nome_escola}", centered_heading))
    elements.append(Paragraph(f"Sala: {aluno.sala.descricao} | Turno: {aluno.sala.turno}", centered_heading1))
    elements.append(Spacer(1, 12))

    # Buscar todos os relatórios do aluno
    relatorios = Relatorio.objects.filter(aluno=aluno).select_related("periodo").order_by("periodo__id")

    if not relatorios.exists():
        elements.append(Paragraph("Nenhum relatório encontrado para este aluno.", styles["Normal"]))
    else:
        body_style = ParagraphStyle(
            'body',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=12
        )

        for idx, rel in enumerate(relatorios, start=1):
            elements.append(Paragraph(f"<b>Período:</b> {rel.periodo}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Professor:</b> {rel.professor or '---'}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Data:</b> {rel.data_relatorio.strftime('%d/%m/%Y')}", styles["Normal"]))
            elements.append(Spacer(1, 6))

            # Texto do relatório
            elements.append(Paragraph(rel.relatorio.replace("\n", "<br/>"), body_style))
            elements.append(Spacer(1, 18))  # espaçamento maior entre relatórios

    # Montar o PDF (quebra de página será automática)
    doc.build(elements)
    return response


###### APIs #####

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_relatorio_registro(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    escola = get_object_or_404(UnidadeEscolar, pk=aluno.sala.escola.pk)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="relatorios_{aluno.nome}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    elements = []
    styles = getSampleStyleSheet()
    centered_heading = ParagraphStyle(name="CenteredHeading2", fontSize=14, leading=18, alignment=TA_CENTER)
    centered_heading1 = ParagraphStyle(name="CenteredHeading2", fontSize=10, leading=18, alignment=TA_CENTER)

    # Cabeçalho
    elements.append(Paragraph(f"<b>{aluno.nome}</b>", styles["Title"]))
    elements.append(Paragraph(f"{escola.nome_escola}", centered_heading))
    elements.append(Paragraph(f"Sala: {aluno.sala.descricao} | Turno: {aluno.sala.turno}", centered_heading1))
    elements.append(Spacer(1, 12))

    # Relatórios
    relatorios = Relatorio.objects.filter(aluno=aluno).select_related("periodo").order_by("periodo__id")
    body_style = ParagraphStyle('body', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=12)

    if not relatorios.exists():
        elements.append(Paragraph("Nenhum relatório encontrado para este aluno.", styles["Normal"]))
    else:
        for rel in relatorios:
            elements.append(Paragraph(f"<b>Período:</b> {rel.periodo}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Professor:</b> {rel.professor or '---'}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Data:</b> {rel.data_relatorio.strftime('%d/%m/%Y')}", styles["Normal"]))
            elements.append(Spacer(1,6))
            elements.append(Paragraph(rel.relatorio.replace("\n","<br/>"), body_style))
            elements.append(Spacer(1,18))

    doc.build(elements)
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_relatorio_frequencia(request, pk, mes):
    # Obter sala, escola e alunos
    sala = get_object_or_404(Sala, pk=pk)
    escola = get_object_or_404(UnidadeEscolar, pk=sala.escola.pk)
    alunos = Aluno.objects.filter(sala=sala).order_by("nome")

    # Criar resposta PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{sala.descricao}.pdf"'

    # Documento paisagem
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )

    # Estilos
    styles = getSampleStyleSheet()
    centered_heading = ParagraphStyle(name="CenteredHeading2", fontSize=14, leading=18, alignment=TA_CENTER)
    centered_heading1 = ParagraphStyle(name="CenteredHeading2", fontSize=12, leading=18, alignment=TA_CENTER)

    elements = []

    # Cabeçalho
    elements.append(Paragraph(f"<b>{escola.nome_escola}</b>", styles["Title"]))
    elements.append(Paragraph(f"{sala.descricao} - {sala.ano}", centered_heading))

    nome_meses = {
        1:'Janeiro',2:'Fevereiro',3:'Março',4:'Abril',5:'Maio',6:'Junho',
        7:'Julho',8:'Agosto',9:'Setembro',10:'Outubro',11:'Novembro',12:'Dezembro'
    }
    elements.append(Paragraph(f"<b>{nome_meses[mes]} - {sala.ano_letivo.ano}</b>", centered_heading1))
    elements.append(Spacer(1, 12))

    # Preparar tabela
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")  # para nomes de dias em português
    ano = sala.ano_letivo.ano
    dias_mes = calendar.monthcalendar(ano, mes)

    # Cabeçalho da tabela
    header_dias = ["Alunos"]
    header_semana = [""]

    for semana in dias_mes:
        for dia in semana:
            if dia != 0:
                data = datetime(ano, mes, dia)
                if data.weekday() < 5:  # dias úteis (segunda a sexta)
                    header_dias.append(data.strftime("%d"))
                    header_semana.append(data.strftime("%a"))

    data_table = [header_dias, header_semana]

    # Preencher linhas com frequência dos alunos
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
                        except FrequenciaAluno.DoesNotExist:
                            linha.append(".")
        data_table.append(linha)

    # Definir largura das colunas
    total_width = 29.7*cm - 2*cm  # largura paisagem menos margens
    nome_col_width = 6*cm
    restantes = len(header_dias) - 1
    col_widths = [nome_col_width] + [(total_width - nome_col_width)/restantes]*restantes

    # Criar tabela
    table = Table(data_table, colWidths=col_widths, repeatRows=2)

    # Estilo da tabela
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

    # Montar PDF
    doc.build(elements)
    return response