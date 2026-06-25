from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin, TabularInline

from .forms import UserCreationForm, UserChangeForm
from .models import Usuario, VinculoEscola, PapelVinculo


class VinculoEscolaInline(TabularInline):
    model           = VinculoEscola
    extra           = 0
    fields          = ('escola', 'ativo', 'data_entrada')
    readonly_fields = ('data_entrada',)


class PapelVinculoInline(TabularInline):
    model  = PapelVinculo
    extra  = 0
    fields = ('tipo', 'ativo')


@admin.register(Usuario)
class UsuarioAdmin(ModelAdmin, BaseUserAdmin):
    form     = UserChangeForm
    add_form = UserCreationForm

    list_display      = ('email', 'nome', 'is_platform_admin', 'is_staff', 'is_active')
    list_filter       = ('is_staff', 'is_active', 'is_platform_admin')
    search_fields     = ('email', 'nome')
    ordering          = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None,                   {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'foto')}),
        ('Permissões',           {'fields': ('is_active', 'is_staff', 'is_superuser',
                                              'is_platform_admin', 'groups', 'user_permissions')}),
        ('Datas',                {'fields': ('data_criacao', 'data_atualizacao')}),
    )
    readonly_fields = ('data_criacao', 'data_atualizacao')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'nome', 'password1', 'password2'),
        }),
    )

    inlines = [VinculoEscolaInline]


@admin.register(VinculoEscola)
class VinculoEscolaAdmin(ModelAdmin):
    list_display    = ('usuario', 'escola', 'ativo', 'data_entrada')
    list_filter     = ('ativo', 'escola')
    search_fields   = ('usuario__email', 'usuario__nome')
    readonly_fields = ('data_entrada',)
    inlines         = [PapelVinculoInline]


@admin.register(PapelVinculo)
class PapelVinculoAdmin(ModelAdmin):
    list_display  = ('vinculo', 'tipo', 'ativo')
    list_filter   = ('tipo', 'ativo')
    search_fields = ('vinculo__usuario__email', 'vinculo__usuario__nome')
