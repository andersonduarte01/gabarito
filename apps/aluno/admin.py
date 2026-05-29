from django.contrib import admin
from .models import Aluno


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('get_nome', 'escola', 'sala', 'situacao', 'sexo')
    list_filter = ('escola', 'situacao', 'sexo', 'sala')
    search_fields = ('usuario__nome', 'usuario__email', 'cpf', 'responsavel_legal')
    raw_id_fields = ('usuario',)

    @admin.display(description='Nome', ordering='usuario__nome')
    def get_nome(self, obj):
        return obj.usuario.nome
