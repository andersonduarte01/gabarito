from django.contrib import admin
from .models import Ano, Sala


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'escola', 'ano', 'turno', 'ano_letivo')
    list_filter = ('escola', 'turno', 'ano')
    search_fields = ('descricao',)


@admin.register(Ano)
class AnoAdmin(admin.ModelAdmin):
    list_display = ('descricao',)
    search_fields = ('descricao',)
