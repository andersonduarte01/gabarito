from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.serie.models import Serie


@admin.register(Serie)
class SerieAdmin(ModelAdmin):
    list_display    = ('nome', 'segmento', 'escola', 'ordem', 'ativo')
    list_filter     = ('ativo', 'segmento__tipo')
    search_fields   = ('nome', 'escola__nome')
    ordering        = ('escola', 'segmento__tipo', 'ordem')
    readonly_fields = ('escola', 'segmento')

    def has_add_permission(self, request):
        return False
