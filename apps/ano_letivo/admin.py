from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import AnoLetivo, PeriodoLetivo


class PeriodoLetivoInline(TabularInline):
    model        = PeriodoLetivo
    extra        = 0
    readonly_fields = ('numero', 'nome', 'data_inicio', 'data_fim')
    can_delete   = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AnoLetivo)
class AnoLetivoAdmin(ModelAdmin):
    list_display  = ('ano', 'escola', 'status', 'data_inicio', 'data_fim', 'criado_por')
    list_filter   = ('status',)
    search_fields = ('escola__nome', 'ano')
    readonly_fields = ('criado_por', 'criado_em', 'atualizado_em')
    inlines       = [PeriodoLetivoInline]
    ordering      = ('-ano', 'escola')


@admin.register(PeriodoLetivo)
class PeriodoLetivoAdmin(ModelAdmin):
    list_display  = ('nome', 'numero', 'ano_letivo', 'data_inicio', 'data_fim')
    search_fields = ('nome', 'ano_letivo__escola__nome')
    ordering      = ('ano_letivo', 'numero')
