from django.contrib import admin
from .models import Frequencia, FrequenciaAluno, Registro, Periodo, Relatorio
# Register your models here.

admin.site.register(Frequencia)
admin.site.register(FrequenciaAluno)
admin.site.register(Registro)
admin.site.register(Periodo)


class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'aluno', 'professor', 'data_relatorio', 'atualiza_relatorio')
    search_fields = ('aluno__nome', 'professor__professor_nome', 'periodo__periodo')  # Ajuste os campos conforme a sua necessidade


admin.site.register(Relatorio, RelatorioAdmin)
