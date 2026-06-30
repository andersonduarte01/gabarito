from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import RelatorioAgendado, RelatorioGerado


@admin.register(RelatorioAgendado)
class RelatorioAgendadoAdmin(ModelAdmin):
    list_display  = ('escola', 'tipo', 'periodicidade', 'ativo', 'criado_em')
    list_filter   = ('tipo', 'periodicidade', 'ativo')
    search_fields = ('escola__nome',)


@admin.register(RelatorioGerado)
class RelatorioGeradoAdmin(ModelAdmin):
    list_display  = ('escola', 'tipo', 'gerado_em', 'arquivo')
    list_filter   = ('tipo',)
    search_fields = ('escola__nome',)
    readonly_fields = ('escola', 'tipo', 'parametros', 'gerado_em', 'arquivo', 'agendado')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
