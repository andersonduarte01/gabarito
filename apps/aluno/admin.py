from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Aluno, MatriculaTurma


class MatriculaTurmaInline(TabularInline):
    model  = MatriculaTurma
    extra  = 0
    fields = ('turma', 'ano_letivo', 'situacao', 'ativo', 'data_matricula')
    readonly_fields = ('data_matricula',)


@admin.register(Aluno)
class AlunoAdmin(ModelAdmin):
    list_display   = ('nome_completo', 'matricula', 'escola', 'ativo', 'criado_em')
    list_filter    = ('escola', 'ativo')
    search_fields  = ('nome_completo', 'matricula', 'cpf')
    readonly_fields = ('matricula', 'criado_em', 'atualizado_em')
    inlines        = [MatriculaTurmaInline]


@admin.register(MatriculaTurma)
class MatriculaTurmaAdmin(ModelAdmin):
    list_display  = ('aluno', 'turma', 'ano_letivo', 'situacao', 'ativo', 'data_matricula')
    list_filter   = ('situacao', 'ativo', 'ano_letivo')
    search_fields = ('aluno__nome_completo', 'aluno__matricula')
    readonly_fields = ('data_matricula',)
