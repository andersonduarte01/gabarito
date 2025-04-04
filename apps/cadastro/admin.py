from django.contrib import admin
from .models import Cadastro, CadastroInicio, CadUnificado, RG, Profissional, Endereco
# Register your models here.


admin.site.register(Cadastro)
admin.site.register(CadastroInicio)
admin.site.register(CadUnificado)
admin.site.register(RG)
admin.site.register(Profissional)
admin.site.register(Endereco)
