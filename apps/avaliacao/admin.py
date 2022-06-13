from django.contrib import admin
from pyexpat import model

from .models import Avaliacao, Questao, Gabarito, Resposta
# Register your models here.
from django.contrib.admin import ModelAdmin


class QuestaoInline(admin.StackedInline):
    model = Questao
    exclude = ('status_questao',)
    extra = 1


class AvaliacaoAdmin(ModelAdmin):
    list_display = ('descricao', 'ano')
    fieldsets = (
        ('Dados Avaliação', {'fields': ['descricao', 'ano']}),
    )
    add_fieldsets = (
        ('Informações da Avaliação', {
            'classes': ('wide',),
            'fields': ('descricao', 'ano'),
        }),
    )
    inlines = [QuestaoInline]


class RespostaAdm(admin.ModelAdmin):
    model = Resposta
    list_display = ('gabarito', 'questao', 'acertou')


admin.site.register(Avaliacao, AvaliacaoAdmin)
admin.site.register(Gabarito)
admin.site.register(Resposta, RespostaAdm)