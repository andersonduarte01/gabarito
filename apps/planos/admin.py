from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import AssinaturaEscola, HistoricoAssinatura, Modulo, ModuloEscola, Plano


class ModuloEscolaInline(TabularInline):
    model   = ModuloEscola
    extra   = 0
    fields  = ('modulo', 'ativo')


class HistoricoAssinaturaInline(TabularInline):
    model           = HistoricoAssinatura
    extra           = 0
    can_delete      = False
    readonly_fields = ('status_anterior', 'status_novo', 'plano_anterior', 'plano_novo',
                       'alterado_por', 'alterado_em', 'observacao')


@admin.register(Modulo)
class ModuloAdmin(ModelAdmin):
    list_display  = ('codigo', 'nome', 'ativo_plataforma')
    list_filter   = ('ativo_plataforma',)
    search_fields = ('codigo', 'nome')


@admin.register(Plano)
class PlanoAdmin(ModelAdmin):
    list_display      = ('nome', 'preco_mensal', 'ativo')
    list_filter       = ('ativo',)
    filter_horizontal = ('modulos',)


@admin.register(AssinaturaEscola)
class AssinaturaEscolaAdmin(ModelAdmin):
    list_display    = ('escola', 'plano', 'status', 'data_vencimento', 'atualizado_em')
    list_filter     = ('status',)
    search_fields   = ('escola__nome_escola',)
    readonly_fields = ('atualizado_em',)
    inlines         = [ModuloEscolaInline, HistoricoAssinaturaInline]


@admin.register(HistoricoAssinatura)
class HistoricoAssinaturaAdmin(ModelAdmin):
    list_display    = ('assinatura', 'status_anterior', 'status_novo', 'alterado_por', 'alterado_em')
    list_filter     = ('status_novo',)
    readonly_fields = ('alterado_em',)
