from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import PerfilResponsavel, VinculoResponsavelAluno


class VinculoAlunoInline(TabularInline):
    model  = VinculoResponsavelAluno
    extra  = 0
    fields = ('aluno', 'parentesco', 'responsavel_principal', 'responsavel_financeiro', 'ativo')


@admin.register(PerfilResponsavel)
class PerfilResponsavelAdmin(ModelAdmin):
    list_display  = ('nome', 'email', 'telefone', 'tem_acesso', 'criado_em')
    list_filter   = ('vinculos_aluno__parentesco',)
    search_fields = ('nome', 'usuario__email', 'cpf')
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines       = [VinculoAlunoInline]

    @admin.display(description='Tem acesso', boolean=True)
    def tem_acesso(self, obj):
        return obj.usuario_id is not None


@admin.register(VinculoResponsavelAluno)
class VinculoResponsavelAlunoAdmin(ModelAdmin):
    list_display  = ('responsavel', 'aluno', 'parentesco', 'responsavel_principal', 'ativo')
    list_filter   = ('parentesco', 'responsavel_principal', 'ativo')
    search_fields = ('responsavel__nome', 'aluno__nome_completo')
