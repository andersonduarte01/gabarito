from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline

from .models import UnidadeEscolar, EnderecoEscolar, AnoLetivo


class EnderecoInline(StackedInline):
    model      = EnderecoEscolar
    extra      = 0
    can_delete = False


class AnoLetivoInline(TabularInline):
    model  = AnoLetivo
    extra  = 0
    fields = ('ano', 'inicio', 'fim', 'corrente')


@admin.register(UnidadeEscolar)
class EscolaAdmin(ModelAdmin):
    list_display        = ('nome_escola', 'tipo', 'cnpj', 'telefone', 'email', 'ativo')
    list_filter         = ('tipo', 'ativo')
    search_fields       = ('nome_escola', 'cnpj', 'inep', 'email')
    prepopulated_fields = {'slug': ('nome_escola',)}
    readonly_fields     = ('criado_em', 'atualizado_em')
    inlines             = [EnderecoInline, AnoLetivoInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('nome_escola', 'slug', 'tipo', 'logo_escola', 'ativo'),
        }),
        ('Dados Oficiais', {
            'fields': ('inep', 'cnpj'),
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'site'),
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',),
        }),
    )


@admin.register(AnoLetivo)
class AnoLetivoAdmin(ModelAdmin):
    list_display  = ('ano', 'escola', 'inicio', 'fim', 'corrente')
    list_filter   = ('corrente', 'escola')
    search_fields = ('escola__nome_escola',)
    ordering      = ('-ano',)
