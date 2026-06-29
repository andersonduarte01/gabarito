from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Turma


@admin.register(Turma)
class TurmaAdmin(ModelAdmin):
    list_display  = ('escola', 'ano_letivo', 'serie', 'nome', 'turno', 'capacidade', 'ativo')
    list_filter   = ('ativo', 'turno', 'ano_letivo__ano')
    search_fields = ('nome', 'escola__nome', 'serie__nome')
