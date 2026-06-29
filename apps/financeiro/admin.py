from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CobrancaAluno, PlanoFinanceiro


@admin.register(PlanoFinanceiro)
class PlanoFinanceiroAdmin(ModelAdmin):
    list_display  = ('nome', 'escola', 'valor', 'periodicidade', 'ativo')
    list_filter   = ('periodicidade', 'ativo')
    search_fields = ('nome', 'escola__nome')


@admin.register(CobrancaAluno)
class CobrancaAlunoAdmin(ModelAdmin):
    list_display  = ('aluno', 'descricao', 'valor', 'vencimento', 'status', 'gateway', 'criado_em')
    list_filter   = ('status', 'gateway')
    search_fields = ('aluno__nome_completo', 'descricao', 'gateway_id')
    readonly_fields = ('criado_em', 'pago_em', 'criado_por')
    date_hierarchy = 'vencimento'
