from django.contrib import admin
from .models import Frequencia, FrequenciaAluno, Registro, Periodo, Relatorio
# Registe

admin.site.register(Registro)
admin.site.register(Periodo)

@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('sala', 'data', 'presentes', 'status')  # colunas visíveis
    list_filter = ('data', 'sala', 'status')  # filtros laterais
    search_fields = ('sala__descricao',)  # busca por nome/descrição da sala
    ordering = ('-data',)

@admin.register(FrequenciaAluno)
class FrequenciaAlunoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'data', 'presente', 'observacao')  # colunas exibidas na lista
    list_filter = ('data', 'presente')  # filtros laterais, permite filtrar por data
    search_fields = ('aluno__nome', 'observacao')

class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'aluno', 'professor', 'data_relatorio', 'atualiza_relatorio')
    search_fields = ('aluno__nome', 'professor__professor_nome', 'periodo__periodo')  # Ajuste os campos conforme a sua necessidade


admin.site.register(Relatorio, RelatorioAdmin)
