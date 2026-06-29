from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    ConfiguracaoAcademica, ConfiguracaoFinanceira,
    ConfiguracaoFrequencia, ConfiguracaoProfessor,
)


@admin.register(ConfiguracaoAcademica)
class ConfiguracaoAcademicaAdmin(ModelAdmin):
    list_display  = ('escola', 'nota_maxima', 'nota_minima_aprovacao',
                     'tipo_periodo_letivo', 'tipo_calculo_media', 'exige_recuperacao')
    search_fields = ('escola__nome',)
    readonly_fields = ('escola',)


@admin.register(ConfiguracaoFrequencia)
class ConfiguracaoFrequenciaAdmin(ModelAdmin):
    list_display  = ('escola', 'percentual_minimo_frequencia',
                     'percentual_alerta_prevencao', 'modo_lancamento')
    search_fields = ('escola__nome',)
    readonly_fields = ('escola',)


@admin.register(ConfiguracaoFinanceira)
class ConfiguracaoFinanceiraAdmin(ModelAdmin):
    list_display  = ('escola', 'multa_percentual', 'juros_percentual_mes',
                     'dias_tolerancia', 'gateway_padrao')
    search_fields = ('escola__nome',)
    readonly_fields = ('escola',)


@admin.register(ConfiguracaoProfessor)
class ConfiguracaoProfessorAdmin(ModelAdmin):
    list_display  = ('escola', 'carga_horaria_maxima_semanal')
    search_fields = ('escola__nome',)
    readonly_fields = ('escola',)
