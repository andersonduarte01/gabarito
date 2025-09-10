from hijack.contrib.admin import HijackUserAdminMixin

from ..core.admin import UserAdmin

from django.contrib import admin
from .models import UnidadeEscolar, EnderecoEscolar, AnoLetivo


class EnderecoInline(admin.StackedInline):
    model = EnderecoEscolar
    extra = 1


class Letivo(admin.ModelAdmin):
    list_display = ('id', 'ano', 'inicio', 'fim', 'corrente')

admin.register(UnidadeEscolar)
class EscolaAdmin(HijackUserAdminMixin, admin.ModelAdmin):
    def get_hijack_user(self, obj):
        return obj

admin.site.register(UnidadeEscolar, EscolaAdmin)
admin.site.register(AnoLetivo, Letivo)
