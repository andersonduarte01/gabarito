from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import Usuario, UsuarioEscola


class UsuarioEscolaInline(admin.TabularInline):
    model = UsuarioEscola
    extra = 0
    fields = ('escola', 'tipo_usuario', 'ativo', 'data_vinculo')
    readonly_fields = ('data_vinculo',)


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'nome', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'nome')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('data_criacao', 'data_atualizacao')}),
    )
    readonly_fields = ('data_criacao', 'data_atualizacao')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2'),
        }),
    )

    inlines = [UsuarioEscolaInline]


@admin.register(UsuarioEscola)
class UsuarioEscolaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'escola', 'tipo_usuario', 'ativo', 'data_vinculo')
    list_filter = ('tipo_usuario', 'ativo', 'escola')
    search_fields = ('usuario__email', 'usuario__nome')
    readonly_fields = ('data_vinculo',)
