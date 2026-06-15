from django.contrib import admin

from .models import Diretor


@admin.register(Diretor)
class DiretorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'escola', 'telefone', 'ativo', 'criado_em')
    list_filter = ('ativo', 'escola')
    search_fields = ('usuario__nome', 'usuario__email', 'escola__nome_escola', 'cpf')
    raw_id_fields = ('usuario', 'escola')
