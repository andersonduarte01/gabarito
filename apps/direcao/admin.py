from django.contrib import admin

# Register your models here.
from apps.direcao.models import DirecaoEscolar
from ..core.admin import UserAdmin


class DirecaoEscolarAdmin(UserAdmin):
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


admin.site.register(DirecaoEscolar, DirecaoEscolarAdmin)
