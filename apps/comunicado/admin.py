from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Comunicado, LeituraComunicado


class LeituraComunicadoInline(TabularInline):
    model  = LeituraComunicado
    extra  = 0
    readonly_fields = ('usuario', 'lido_em')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Comunicado)
class ComunicadoAdmin(ModelAdmin):
    list_display  = ('titulo', 'escola', 'tipo', 'destinatarios', 'publicada', 'criado_em')
    list_filter   = ('tipo', 'destinatarios', 'publicada')
    search_fields = ('titulo', 'escola__nome')
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines       = [LeituraComunicadoInline]
