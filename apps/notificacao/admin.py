from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Notificacao


@admin.register(Notificacao)
class NotificacaoAdmin(ModelAdmin):
    list_display    = ('destinatario', 'titulo', 'tipo', 'lida', 'criado_em')
    list_filter     = ('tipo', 'lida')
    search_fields   = ('destinatario__nome', 'destinatario__email', 'titulo')
    readonly_fields = ('destinatario', 'titulo', 'mensagem', 'tipo', 'lida', 'criado_em')
    ordering        = ('-criado_em',)

    def has_add_permission(self, request):
        return False
