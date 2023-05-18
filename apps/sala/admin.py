from django.contrib import admin

# Register your models here.
from ..sala.models import Ano, Sala


class SalaAdmin(admin.ModelAdmin):
    model = Sala
    list_display = ['descricao', 'escola', 'ano']


admin.site.register(Sala, SalaAdmin)
admin.site.register(Ano)
