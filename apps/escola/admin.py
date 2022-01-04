from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UnidadeEscolar
# Register your models here.
from ..core.admin import UserAdmin


# @admin.register(UnidadeEscolar)
# class EscolaAdmin(UserAdmin):
#     model = UnidadeEscolar
#     list_display = ('email', 'nome_escola')

from django.contrib import admin
from .models import UnidadeEscolar, EnderecoEscolar


class EnderecoInline(admin.StackedInline):
    model = EnderecoEscolar
    extra = 1


class EscolaAdmin(UserAdmin):
    list_display = ('nome_escola', 'inep', 'email', 'cadastrado_em')
    fieldsets = (
        ('Dados Básicos', {'fields': ['nome_escola', 'inep', 'cnpj']}),
        ('Informações de Contato', {'fields': ['email', 'telefone']}),
    )
    add_fieldsets = (
        ('Informações da Escola', {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2', 'nome_escola', 'logo_escola', 'inep', 'cnpj', 'telefone'),
        }),
    )
    inlines = [EnderecoInline]

admin.site.register(UnidadeEscolar, EscolaAdmin)
