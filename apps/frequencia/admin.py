from django.contrib import admin
from .models import Frequencia, FrequenciaAluno, Registro, Periodo, Relatorio
# Register your models here.

admin.site.register(Frequencia)
admin.site.register(FrequenciaAluno)
admin.site.register(Registro)
admin.site.register(Periodo)
admin.site.register(Relatorio)
