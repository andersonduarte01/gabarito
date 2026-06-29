from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import PerfilDiretor


@admin.register(PerfilDiretor)
class PerfilDiretorAdmin(ModelAdmin):
    list_display  = ('__str__', 'cargo', 'cpf', 'telefone', 'criado_em')
    list_filter   = ('cargo',)
    search_fields = ('papel__vinculo__usuario__nome', 'papel__vinculo__usuario__email',
                     'papel__vinculo__escola__nome', 'cpf')
    readonly_fields = ('criado_em', 'atualizado_em')

    fieldsets = (
        ('Vínculo', {
            'fields': ('papel',),
        }),
        ('Dados Pessoais', {
            'fields': ('cpf', 'data_nascimento', 'telefone', 'foto'),
        }),
        ('Cargo', {
            'fields': ('cargo', 'numero_ato', 'data_ato', 'data_inicio'),
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',),
        }),
    )
