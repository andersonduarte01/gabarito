from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Evento, LeituraEvento


class LeituraEventoInline(TabularInline):
    model   = LeituraEvento
    extra   = 0
    readonly_fields = ('usuario', 'lido_em')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Evento)
class EventoAdmin(ModelAdmin):
    list_display  = ('titulo', 'escola', 'tipo', 'data_inicio', 'destinatarios', 'publicada')
    list_filter   = ('tipo', 'destinatarios', 'publicada')
    search_fields = ('titulo', 'escola__nome')
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines       = [LeituraEventoInline]
