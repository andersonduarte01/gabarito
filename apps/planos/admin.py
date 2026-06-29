from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import AssinaturaEscola, HistoricoAssinatura, Modulo, ModuloEscola, Plano, StatusAssinatura


class ModuloEscolaInline(TabularInline):
    model   = ModuloEscola
    extra   = 0
    fields  = ('modulo', 'ativo')


class HistoricoAssinaturaInline(TabularInline):
    model           = HistoricoAssinatura
    extra           = 0
    can_delete      = False
    readonly_fields = ('status_anterior', 'status_novo', 'plano_anterior', 'plano_novo',
                       'alterado_por', 'alterado_em', 'observacao')


@admin.register(Modulo)
class ModuloAdmin(ModelAdmin):
    list_display  = ('codigo', 'nome', 'ativo_plataforma')
    list_filter   = ('ativo_plataforma',)
    search_fields = ('codigo', 'nome')


@admin.register(Plano)
class PlanoAdmin(ModelAdmin):
    list_display      = ('nome', 'preco_mensal', 'ativo')
    list_filter       = ('ativo',)
    filter_horizontal = ('modulos',)


@admin.register(AssinaturaEscola)
class AssinaturaEscolaAdmin(ModelAdmin):
    list_display    = ('escola', 'plano', 'status', 'data_vencimento', 'atualizado_em')
    list_filter     = ('status',)
    search_fields   = ('escola__nome',)
    readonly_fields = ('atualizado_em',)
    inlines         = [ModuloEscolaInline, HistoricoAssinaturaInline]

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            # Novo registro: exibe todos os campos — admin escolhe o que preencher
            return [
                ('Assinatura', {
                    'fields': ('escola', 'plano', 'status'),
                }),
                ('Vigência (plano pago)', {
                    'fields': ('data_inicio', 'data_vencimento', 'data_grace_fim', 'ativado_por'),
                    'description': 'Preencha ao criar uma assinatura já ativa.',
                }),
                ('Trial', {
                    'fields': ('data_inicio_trial', 'duracao_trial_dias', 'limite_alunos_trial'),
                    'description': 'Deixe em branco se a escola já possui plano pago.',
                }),
                ('Auditoria', {
                    'fields': ('atualizado_em',),
                }),
            ]

        status_trial = {StatusAssinatura.TRIAL, StatusAssinatura.TRIAL_EXPIRADO}
        if obj.status in status_trial:
            return [
                ('Assinatura', {
                    'fields': ('escola', 'plano', 'status'),
                }),
                ('Trial', {
                    'fields': ('data_inicio_trial', 'duracao_trial_dias', 'limite_alunos_trial'),
                }),
                ('Auditoria', {
                    'fields': ('atualizado_em',),
                }),
            ]

        return [
            ('Assinatura', {
                'fields': ('escola', 'plano', 'status'),
            }),
            ('Vigência', {
                'fields': ('data_inicio', 'data_vencimento', 'data_grace_fim', 'ativado_por'),
            }),
            ('Auditoria', {
                'fields': ('atualizado_em',),
            }),
        ]


@admin.register(HistoricoAssinatura)
class HistoricoAssinaturaAdmin(ModelAdmin):
    list_display    = ('assinatura', 'status_anterior', 'status_novo', 'alterado_por', 'alterado_em')
    list_filter     = ('status_novo',)
    readonly_fields = ('alterado_em',)
