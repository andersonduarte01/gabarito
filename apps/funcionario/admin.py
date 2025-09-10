from django.contrib import admin
from hijack.contrib.admin import HijackUserAdminMixin

from ..funcionario.models import Funcionario, Professor

@admin.register(Funcionario)
class FuncionarioAdmin(HijackUserAdminMixin, admin.ModelAdmin):
    def get_hijack_user(self, obj):
        return obj

    list_display = ('escola', 'nome', 'email', 'funcao')
    list_filter = ('nome', 'escola')
    search_fields = ('nome', 'escola')
    ordering = ('nome',)

@admin.register(Professor)
class ProfessorAdmin(HijackUserAdminMixin, admin.ModelAdmin):
    # Função obrigatória para o hijack
    def get_hijack_user(self, obj):
        return obj

    # Mantendo as configurações antigas
    list_display = ('professor_nome', 'email', 'is_professor')
    list_filter = ('professor_nome', )
    search_fields = ('professor_nome', 'email')
    ordering = ('professor_nome',)
