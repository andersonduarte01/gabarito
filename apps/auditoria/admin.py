from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import LogAuditoria


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(ModelAdmin):
    list_display    = ('criado_em', 'usuario', 'escola', 'acao', 'modelo', 'objeto_id', 'ip')
    list_filter     = ('acao',)
    search_fields   = ('usuario__nome', 'usuario__email', 'escola__nome', 'modelo', 'descricao')
    readonly_fields = (
        'usuario', 'escola', 'papel_tipo', 'acao', 'modelo',
        'objeto_id', 'descricao', 'ip', 'criado_em',
    )
    ordering = ('-criado_em',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
