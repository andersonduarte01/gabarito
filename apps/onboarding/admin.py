from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ConviteOnboarding


@admin.register(ConviteOnboarding)
class ConviteOnboardingAdmin(ModelAdmin):
    list_display  = ('escola', 'email', 'canal_envio', 'usado', 'criado_em', 'expira_em')
    list_filter   = ('usado', 'canal_envio')
    search_fields = ('escola__nome', 'email')
    readonly_fields = ('token', 'criado_em', 'expira_em')

    def has_add_permission(self, request):
        return False
