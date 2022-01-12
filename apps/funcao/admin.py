from django.contrib import admin

# Register your models here.
from .models import Funcao


@admin.register(Funcao)
class FuncaoADM(admin.ModelAdmin):
    list_display = ('codigo','funcao', 'escola')
    list_filter = ('escola',)
