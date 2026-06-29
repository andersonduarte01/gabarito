from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import PresencaAluno, RegistroFrequencia


class PresencaAlunoInline(TabularInline):
    model  = PresencaAluno
    extra  = 0
    fields = ('aluno', 'presente', 'justificado', 'observacao')


@admin.register(RegistroFrequencia)
class RegistroFrequenciaAdmin(ModelAdmin):
    list_display  = ('turma', 'materia', 'data', 'ano_letivo', 'periodo_letivo', 'criado_por')
    list_filter   = ('ano_letivo', 'periodo_letivo', 'turma')
    search_fields = ('turma__nome', 'materia__nome')
    readonly_fields = ('criado_em',)
    inlines       = [PresencaAlunoInline]


@admin.register(PresencaAluno)
class PresencaAlunoAdmin(ModelAdmin):
    list_display  = ('aluno', 'registro', 'presente', 'justificado')
    list_filter   = ('presente', 'justificado')
    search_fields = ('aluno__nome_completo',)
