from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline

from .models import EnderecoEscolar, SegmentoEscolar, UnidadeEscolar


class SegmentoInline(TabularInline):
    model      = SegmentoEscolar
    extra      = 0
    fields     = ('tipo',)


class EnderecoInline(StackedInline):
    model      = EnderecoEscolar
    extra      = 0
    fields     = ('nome', 'principal', 'cep', 'logradouro', 'numero',
                  'complemento', 'bairro', 'municipio', 'uf')


@admin.register(UnidadeEscolar)
class EscolaAdmin(ModelAdmin):
    list_display        = ('nome', 'tipo', 'cnpj', 'municipio', 'uf', 'criado_em')
    list_filter         = ('tipo',)
    search_fields       = ('nome', 'cnpj', 'email')
    prepopulated_fields = {'slug': ('nome',)}
    readonly_fields     = ('criado_em', 'atualizado_em')
    inlines             = [SegmentoInline, EnderecoInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'nome_curto', 'slug', 'tipo', 'logo'),
        }),
        ('Dados Oficiais', {
            'fields': ('cnpj',),
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'site'),
        }),
        ('Localização (referência rápida)', {
            'fields': ('municipio', 'uf'),
            'description': 'Atualizado automaticamente ao definir o endereço principal.',
        }),
        ('Identidade Visual', {
            'fields': ('cor_primaria', 'cor_secundaria', 'cor_acento'),
            'classes': ('collapse',),
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',),
        }),
    )
