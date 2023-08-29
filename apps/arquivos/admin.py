from django.contrib import admin
from .models import Arquivo, Livro, Categoria

# Register your models here.
admin.site.register(Arquivo)
admin.site.register(Livro)
admin.site.register(Categoria)
