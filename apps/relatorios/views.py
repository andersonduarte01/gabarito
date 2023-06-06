import os
import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from django.template.loader import render_to_string
from django.views.generic import View
from .conversor import html_to_pdf, html_to_pdf2, html_to_pdf1
from ..aluno import models
from ..aluno.models import Aluno
from ..avaliacao.models import Avaliacao, Gabarito, Questao
from ..escola.models import UnidadeEscolar
from ..sala.models import Sala


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        pdf = html_to_pdf('relatorios/result.html')

        return HttpResponse(pdf, content_type='application/pdf')


class GeneratePdf1(View):
    def get(self, request, *args, **kwargs):
        pdf = html_to_pdf1('relatorios/result1.html')

        return HttpResponse(pdf, content_type='application/pdf')


class GeneratePdf2(View):
    def get(self, request, *args, **kwargs):
        data = models.Aluno.objects.all().order_by('nome')
        open('templates/temp.html', "w", encoding='UTF-8').write(render_to_string('relatorios/result2.html', {'data': data}))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf2('temp.html')

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')


# class RelatorioEscola(View):
#     def get(self, request, *args, **kwargs):
#         data = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
#         salas = get_list_or_404(Sala, escola=data)
#         open('templates/temp.html', "w", encoding='UTF-8').write(render_to_string
#                                                                  ('relatorios/relatorio_escolas.html', {'data': data, 'salas': salas }))
#
#         # Converting the HTML template into a PDF file
#         pdf = html_to_pdf2('temp.html')
#
#         # rendering the template
#         return HttpResponse(pdf, content_type='application/pdf')

class RelatorioEscola(View):
    def get(self, request, *args, **kwargs):
        data = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        salas = Sala.objects.filter(escola=data).order_by('ano')

        open('templates/temp.html', "w", encoding='UTF-8').write(render_to_string
                                                                 ('relatorios/relatorio.html', {'data': data, 'salas': salas}))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf2('temp.html')

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')


class RelatorioSala1(View):
    def get(self, request, *args, **kwargs):
        data = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        sala = get_object_or_404(Sala, pk=self.kwargs['pk'])
        avaliacao = get_object_or_404(Avaliacao, pk=self.kwargs['avaliacao_id'])
        alunos = get_list_or_404(Aluno, sala=sala)
        questoes = len(Questao.objects.filter(avaliacao=avaliacao))
        try:
            gabaritos = get_list_or_404(Gabarito, avaliacao=avaliacao, aluno__in=alunos)
        except:
            gabaritos = []

        # open('templates/temp.html', "w", encoding='UTF-8').write(render_to_string
        #                                                          ('relatorios/relatorio_sala.html', {'data': data, 'gabaritos': gabaritos, 'questoes': questoes}))
        #
        open('/home/anderson/projeto/gabarito/templates/temp.html', "w", encoding='UTF-8').write(render_to_string
                                                                         ('relatorios/relatorio_sala.html', {'data': data, 'gabaritos': gabaritos, 'questoes': questoes}))

        # Converting the HTML template into a PDF file
        # pdf = html_to_pdf2('temp.html')
        pdf = html_to_pdf2('/home/anderson/projeto/gabarito/templates/temp.html')
        os.remove('/home/anderson/projeto/gabarito/templates/temp.html')
        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')


class RelatorioSala(View):
    def get(self, request, *args, **kwargs):
        # Your existing code...
        data = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        sala = get_object_or_404(Sala, pk=self.kwargs['pk'])
        avaliacao = get_object_or_404(Avaliacao, pk=self.kwargs['avaliacao_id'])
        alunos = get_list_or_404(Aluno, sala=sala)
        questoes = len(Questao.objects.filter(avaliacao=avaliacao))
        try:
            gabaritos = get_list_or_404(Gabarito, avaliacao=avaliacao, aluno__in=alunos)
        except:
            gabaritos = []
        # Generate a unique file name using timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"temp_{timestamp}.html"
        file_path = os.path.join('/home/anderson/projeto/gabarito/templates/', file_name)

        # Save the HTML template with the unique file name
        open(file_path, "w", encoding='UTF-8').write(render_to_string('relatorios/relatorio_sala.html', {'data': data, 'gabaritos': gabaritos, 'questoes': questoes}))

        # Generate a unique file name for the PDF
        pdf_file_name = f"relatorio_{timestamp}.pdf"
        pdf_file_path = os.path.join('/home/anderson/projeto/gabarito/templates/', pdf_file_name)

        # Convert the HTML template into a PDF file
        pdf = html_to_pdf2(file_path)

        # Save the PDF with the unique file name
        open(pdf_file_path, "wb").write(pdf)

        # Delete the temporary HTML file
        os.remove(file_path)

        # Serve the PDF file as a response
        with open(pdf_file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename={pdf_file_name}'

        # Delete the temporary PDF file
        os.remove(pdf_file_path)

        return response


class RelatorioAvaliacao(View):
    def get(self, request, *args, **kwargs):
        data = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        sala = get_object_or_404(Sala, pk=self.kwargs['id'])
        avaliacao = get_object_or_404(Avaliacao, pk=self.kwargs['avaliacao_id'])

        open('templates/temp.html', "w", encoding='UTF-8').write(render_to_string
                                                                 ('relatorios/relatorio_avaliacao.html', {'data': data, 'sala': sala, 'avaliacao': avaliacao}))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf2('temp.html')

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')


class RelatorioAluno(View):
    def get(self, request, *args, **kwargs):
        avaliacao = get_object_or_404(Avaliacao, pk=self.kwargs['avaliacao_aluno'])
        aluno = get_object_or_404(Aluno, pk=self.kwargs['aluno'])
        data = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        gabarito = get_object_or_404(Gabarito, avaliacao=avaliacao, aluno=aluno)

        open('templates/temp.html', "w", encoding='UTF-8').write(render_to_string
                                                                 ('relatorios/relatorio_aluno.html', {'data': data, 'avaliacao': avaliacao, 'gabarito': gabarito }))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf2('temp.html')

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')