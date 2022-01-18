from django.contrib import admin

# Register your models here.
from apps.funcionario.models import Funcionario
from ..core.admin import UserAdmin


class FuncionarioAdmin(UserAdmin):
    list_display = ('escola', 'nome', 'funcao', 'email')
    list_filter = ('escola', )
    fieldsets = (
        ('Dados Básicos', {'fields': ['escola', 'funcao', 'nome']}),
    )
    add_fieldsets = (
        ('Informações da Escola', {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2', 'is_funcionario', 'escola'),
        }),
    )


admin.site.register(Funcionario, FuncionarioAdmin)
