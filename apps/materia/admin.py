from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.materia.models import Materia, MateriaSerieConfig


class MateriaSerieConfigInline(TabularInline):
    model  = MateriaSerieConfig
    extra  = 0
    fields = ('serie', 'ativo')
    readonly_fields = ('serie',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Materia)
class MateriaAdmin(ModelAdmin):
    list_display    = ('nome', 'codigo', 'escola', 'ativo')
    list_filter     = ('ativo',)
    search_fields   = ('nome', 'codigo', 'escola__nome')
    ordering        = ('escola', 'nome')
    readonly_fields = ('escola',)
    inlines         = [MateriaSerieConfigInline]

    def has_add_permission(self, request):
        return False


@admin.register(MateriaSerieConfig)
class MateriaSerieConfigAdmin(ModelAdmin):
    list_display  = ('materia', 'serie', 'ativo')
    list_filter   = ('ativo',)
    readonly_fields = ('materia', 'serie')

    def has_add_permission(self, request):
        return False
