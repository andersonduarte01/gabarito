from unfold.admin import ModelAdmin, TabularInline
from django.contrib import admin

from .models import FormacaoAcademica, PerfilProfessor


class FormacaoAcademicaInline(TabularInline):
    model  = FormacaoAcademica
    extra  = 0
    fields = ('nivel', 'curso', 'instituicao', 'ano_conclusao')


@admin.register(PerfilProfessor)
class PerfilProfessorAdmin(ModelAdmin):
    list_display  = ('get_nome', 'get_escola', 'tipo_vinculo', 'get_ativo')
    list_filter   = ('tipo_vinculo', 'papel__ativo')
    search_fields = ('papel__vinculo__usuario__nome', 'papel__vinculo__usuario__email', 'cpf')
    raw_id_fields = ('papel', 'endereco')
    inlines       = [FormacaoAcademicaInline]

    @admin.display(description='Nome', ordering='papel__vinculo__usuario__nome')
    def get_nome(self, obj):
        return obj.usuario.nome

    @admin.display(description='Escola', ordering='papel__vinculo__escola__nome')
    def get_escola(self, obj):
        return obj.escola

    @admin.display(description='Ativo', boolean=True)
    def get_ativo(self, obj):
        return obj.papel.ativo
