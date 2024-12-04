from ..core.admin import UserAdmin

from django.contrib import admin
from .models import UnidadeEscolar, EnderecoEscolar, AnoLetivo


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


class Letivo(admin.ModelAdmin):
    list_display = ('id', 'ano', 'inicio', 'fim')


admin.site.register(UnidadeEscolar, EscolaAdmin)
admin.site.register(AnoLetivo, Letivo)
