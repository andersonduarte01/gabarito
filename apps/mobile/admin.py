from django.contrib import admin

from ..mobile.models import MobileTecnico, MobileUsuario, Chamada

# Register your models here.

admin.site.register(MobileTecnico)
admin.site.register(MobileUsuario)
admin.site.register(Chamada)