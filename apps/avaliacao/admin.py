from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Avaliacao, NotaAluno, OpcaoResposta, Questao, RespostaAluno


class OpcaoRespostaInline(TabularInline):
    model  = OpcaoResposta
    extra  = 0
    fields = ('letra', 'texto', 'correta')


class QuestaoInline(TabularInline):
    model  = Questao
    extra  = 0
    fields = ('numero', 'tipo', 'pontuacao', 'enunciado')


@admin.register(Avaliacao)
class AvaliacaoAdmin(ModelAdmin):
    list_display  = ('titulo', 'turma', 'materia', 'tipo', 'modalidade', 'data_aplicacao', 'publicada')
    list_filter   = ('tipo', 'modalidade', 'publicada', 'escola')
    search_fields = ('titulo',)
    inlines       = [QuestaoInline]


@admin.register(Questao)
class QuestaoAdmin(ModelAdmin):
    list_display  = ('avaliacao', 'numero', 'tipo', 'pontuacao')
    list_filter   = ('tipo',)
    inlines       = [OpcaoRespostaInline]


@admin.register(NotaAluno)
class NotaAlunoAdmin(ModelAdmin):
    list_display  = ('avaliacao', 'aluno', 'nota', 'ausente', 'lancado_em')
    list_filter   = ('ausente', 'avaliacao__escola')
    search_fields = ('aluno__nome_completo',)
    readonly_fields = ('lancado_em',)
