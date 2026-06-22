from django.contrib import admin
from .models import Turma


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'escola', 'serie', 'turno', 'ano_letivo', 'ativo')
    list_filter   = ('escola', 'turno', 'serie', 'ativo')
    search_fields = ('nome',)
