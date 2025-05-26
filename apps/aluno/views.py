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


def relatorioFrequencia(request, pk, mes):
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

    mes_texto = c.stringWidth(f'{nome_meses[mes]} - 2025', "Helvetica", 14)


    escrever_texto(c, texto=f'{nome_meses[mes]} - 2025',
                   x=((ponto3[0] - mes_texto) / 2),
                   y=(ponto3[1] - 85), font="Helvetica", font_size=14,
                   color=(0, 0, 0))

    altura1 = adicionar_linha_paralela(c, ponto3, ponto4, intervalo=118.65)

    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

    ano = 2025
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

        resultado.append(alunos_tag)


    largura_disponivel = (27 * 28.35)
    percorrer = largura_disponivel
    larguras_colunas = [188.95]

    while(percorrer > 1):
        larguras_colunas.append(25)
        percorrer -= 25

    if len(resultado) <= 25:
        t = Table(resultado, colWidths=larguras_colunas)
        largura_tabela, altura_tabela = t.wrapOn(None, largura_disponivel, 0)
        t.setStyle(style)
        largura_tabela = 27 * 28.35
        t.wrapOn(c, largura_tabela, 100)
        t.drawOn(c, ponto1[0] + (((27 * 28.35) - largura_tabela) / 2), altura1 - (altura_tabela - 30))
    else:
        pagina1 = resultado[:26]
        t = Table(pagina1, colWidths=larguras_colunas)
        largura_tabela, altura_tabela = t.wrapOn(None, largura_disponivel, 0)
        t.setStyle(style)
        largura_tabela = 27 * 28.35
        t.wrapOn(c, largura_tabela, 100)
        t.drawOn(c, ponto1[0] + (((27 * 28.35) - largura_tabela) / 2), altura1 - (altura_tabela - 30))

        c.showPage()
        ponto1, ponto2, ponto3, ponto4 = desenhar_retangulo(c)

        pagina2 = []
        pagina2.append(resultado[0])
        pagina2.append(resultado[1])
        p3 = resultado[26:]
        for p in p3:
            pagina2.append(p)

        t = Table(pagina2, colWidths=larguras_colunas)
        largura_tabela, altura_tabela = t.wrapOn(None, largura_disponivel, 0)
        t.setStyle(style)
        largura_tabela = 27 * 28.35
        t.wrapOn(c, largura_tabela, 100)
        t.drawOn(c, ponto1[0] + (((27 * 28.35) - largura_tabela) / 2), ponto4[1] - altura_tabela)


    c.save()
    return response


def relatorioRegistro(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    escola = get_object_or_404(UnidadeEscolar, pk=aluno.sala.escola.pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{aluno}.pdf"'
    # Dimensões da página e do paralelogramo


    c = canvas.Canvas(response, pagesize=A4)
    ponto1, ponto2, ponto3, ponto4 = desenhar_retangulo(c)
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
