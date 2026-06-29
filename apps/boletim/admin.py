from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ResultadoAnual, ResultadoPeriodo


@admin.register(ResultadoPeriodo)
class ResultadoPeriodoAdmin(ModelAdmin):
    list_display  = ('aluno', 'materia', 'periodo_letivo', 'media_periodo', 'frequencia_percentual', 'situacao_periodo', 'calculado_em')
    list_filter   = ('situacao_periodo', 'ano_letivo', 'periodo_letivo')
    search_fields = ('aluno__nome_completo', 'materia__nome')
    readonly_fields = ('calculado_em',)


@admin.register(ResultadoAnual)
class ResultadoAnualAdmin(ModelAdmin):
    list_display  = ('aluno', 'materia', 'ano_letivo', 'media_anual', 'frequencia_anual', 'situacao_final', 'calculado_em')
    list_filter   = ('situacao_final', 'ano_letivo')
    search_fields = ('aluno__nome_completo', 'materia__nome')
    readonly_fields = ('calculado_em',)
