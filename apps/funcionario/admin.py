from django.contrib import admin

# Register your models here.
from ..funcionario.models import Funcionario, Professor
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


class ProfessorAdmin(UserAdmin):
    list_display = ('professor_nome', 'email', 'is_professor')
    list_filter = ('professor_nome', )


admin.site.register(Professor, ProfessorAdmin)
