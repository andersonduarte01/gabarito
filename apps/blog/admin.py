from django.contrib import admin
from .models import Noticia, Categoria


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'categoria', 'status', 'destaque', 'criado_em']
    list_display_links = ['titulo']
    list_filter = ['status', 'destaque', 'categoria']
    list_editable = ['status', 'destaque']
    search_fields = ['titulo', 'resumo']
    date_hierarchy = 'criado_em'
    ordering = ['-criado_em']
    readonly_fields = ['slug', 'criado_em', 'atualizado_em']

    fieldsets = (
        ('Conteúdo', {'fields': ('titulo', 'resumo', 'conteudo', 'imagem')}),
        ('Publicação', {'fields': ('status', 'destaque', 'categoria')}),
        ('Metadados', {'fields': ('slug', 'autor', 'criado_em', 'atualizado_em'), 'classes': ('collapse',)}),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('titulo',)}
    ordering = ['titulo']
