from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from django.template.loader import render_to_string
from django.views.generic import View
from .conversor import html_to_pdf, html_to_pdf2, html_to_pdf1
from ..aluno import models
from ..aluno.models import Aluno
from ..avaliacao.models import Avaliacao, Gabarito
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
                                                                 ('relatorios/relatorio.html', {'data': data, 'salas': salas }))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf2('temp.html')

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')


class RelatorioSala(View):
    def get(self, request, *args, **kwargs):
        data = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        sala = get_object_or_404(Sala, pk=self.kwargs['pk'])

        open('templates/temp.html', "w", encoding='UTF-8').write(render_to_string
                                                                 ('relatorios/relatorio_sala.html', {'data': data, 'sala': sala }))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf2('temp.html')

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')


class RelatorioAluno(View):
    def get(self, request, *args, **kwargs):
        data = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        avaliacao = get_object_or_404(Avaliacao, pk=self.kwargs['avaliacao_id'])
        aluno = get_object_or_404(Aluno, pk=self.kwargs['pk'])
        gabarito = get_object_or_404(Gabarito, avaliacao=avaliacao, aluno=aluno)

        open('templates/temp.html', "w", encoding='UTF-8').write(render_to_string
                                                                 ('relatorios/relatorio_aluno.html', {'data': data, 'avaliacao': avaliacao, 'gabarito': gabarito }))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf2('temp.html')

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')