from django.contrib import admin
from .models import Serie, Turma


@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'escola', 'ordem')
    list_filter   = ('escola',)
    search_fields = ('nome',)
    ordering      = ('escola', 'ordem', 'nome')


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'escola', 'serie', 'turno', 'ano_letivo', 'ativo')
    list_filter   = ('escola', 'turno', 'serie', 'ativo')
    search_fields = ('nome',)
