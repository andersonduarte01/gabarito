from unfold.admin import ModelAdmin
from django.contrib import admin

from .models import FuncaoEscolar, PerfilColaborador


@admin.register(FuncaoEscolar)
class FuncaoEscolarAdmin(ModelAdmin):
    list_display  = ('nome', 'escola', 'ativo')
    list_filter   = ('ativo', 'escola')
    search_fields = ('nome', 'escola__nome')
    ordering      = ('escola', 'nome')


@admin.register(PerfilColaborador)
class PerfilColaboradorAdmin(ModelAdmin):
    list_display  = ('get_nome', 'get_escola', 'funcao', 'tipo_vinculo', 'get_ativo')
    list_filter   = ('tipo_vinculo', 'papel__ativo')
    search_fields = ('papel__vinculo__usuario__nome', 'papel__vinculo__usuario__email', 'cpf')
    raw_id_fields = ('papel', 'funcao', 'endereco')

    @admin.display(description='Nome', ordering='papel__vinculo__usuario__nome')
    def get_nome(self, obj):
        return obj.usuario.nome

    @admin.display(description='Escola', ordering='papel__vinculo__escola__nome')
    def get_escola(self, obj):
        return obj.escola

    @admin.display(description='Ativo', boolean=True)
    def get_ativo(self, obj):
        return obj.papel.ativo
