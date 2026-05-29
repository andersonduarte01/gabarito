from django.contrib import admin

# Register your models here.
from .models import Funcao


@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin):
    list_display = ('funcao', 'codigo', 'escola')
    list_filter = ('escola',)
    search_fields = ('funcao', 'codigo')
