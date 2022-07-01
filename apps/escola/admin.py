from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UnidadeEscolar
# Register your models here.
from ..core.admin import UserAdmin

from django.contrib import admin
from .models import UnidadeEscolar, EnderecoEscolar


class EnderecoInline(admin.StackedInline):
    model = EnderecoEscolar
    extra = 1


class EscolaAdmin(UserAdmin):
    list_display = ('nome_escola', 'inep', 'email', 'cadastrado_em')
    fieldsets = (
        ('Dados Básicos', {'fields': ['nome_escola', 'slug', 'logo_escola', 'inep', 'cnpj']}),
        ('Informações de Contato', {'fields': ['email', 'telefone', 'is_administrator']}),
    )
    add_fieldsets = (
        ('Informações da Escola', {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2', 'is_administrator', 'nome_escola', 'slug', 'logo_escola', 'inep', 'cnpj', 'telefone'),
        }),
    )
    prepopulated_fields = {'slug': ('nome_escola',)}
    inlines = [EnderecoInline]


admin.site.register(UnidadeEscolar, EscolaAdmin)
