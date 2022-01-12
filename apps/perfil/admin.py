from django.contrib import admin

# Register your models here.
from apps.perfil.models import Pessoa, Endereco

admin.site.register(Pessoa)
admin.site.register(Endereco)
