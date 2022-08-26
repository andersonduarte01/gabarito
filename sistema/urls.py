from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('apps.core.urls', namespace='core')),
    path('escola/', include('apps.escola.urls', namespace='escola')),
    path('funcionario/', include('apps.funcionario.urls', namespace='funcionario')),
    path('perfil/', include('apps.perfil.urls', namespace='perfil')),
    path('funcao/', include('apps.funcao.urls', namespace='funcao')),
    path('avaliacao/', include('apps.avaliacao.urls', namespace='avaliacao')),
    path('salas/', include('apps.sala.urls', namespace='salas')),
    path('aluno/', include('apps.aluno.urls', namespace='alunos')),
    path('relatorio/', include('apps.relatorios.urls', namespace='relatorios')),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('tinymce/', include('tinymce.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
