from django.contrib import admin
from .models import Blog, Categoria, Video
# Register your models here.


class BlogAdmin(admin.ModelAdmin):
    exclude = ['data', 'data_atualizacao']
    prepopulated_fields = {'slug': ('titulo',)}

class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('titulo',)}

admin.site.register(Blog, BlogAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Video)