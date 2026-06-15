from django.contrib import admin
from .models import Arquivo, CategoriaArquivo, Livro, Video

admin.site.register(Arquivo)
admin.site.register(Livro)
admin.site.register(CategoriaArquivo)
admin.site.register(Video)
