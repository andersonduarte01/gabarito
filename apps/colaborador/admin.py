from django.contrib import admin
from .models import Colaborador, Professor


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('get_nome', 'escola', 'funcao', 'get_email', 'ativo', 'criado_em')
    list_filter = ('escola', 'ativo', 'funcao')
    search_fields = ('usuario__nome', 'usuario__email', 'cpf')
    raw_id_fields = ('usuario',)
    autocomplete_fields = ('funcao',)

    @admin.display(description='Nome', ordering='usuario__nome')
    def get_nome(self, obj):
        return obj.usuario.nome

    @admin.display(description='E-mail')
    def get_email(self, obj):
        return obj.usuario.email


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('get_nome', 'escola', 'get_email', 'ativo', 'criado_em')
    list_filter = ('escola', 'ativo')
    search_fields = ('usuario__nome', 'usuario__email', 'cpf')
    raw_id_fields = ('usuario',)

    @admin.display(description='Nome', ordering='usuario__nome')
    def get_nome(self, obj):
        return obj.usuario.nome

    @admin.display(description='E-mail')
    def get_email(self, obj):
        return obj.usuario.email
