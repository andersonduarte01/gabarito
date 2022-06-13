from django.contrib import admin

# Register your models here.
from ..sala.models import Ano, Sala

admin.site.register(Sala)
admin.site.register(Ano)
