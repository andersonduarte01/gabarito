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
    path('pdf/', include('apps.arquivos.urls', namespace='arquivos')),
    path('frequencia/', include('apps.frequencia.urls', namespace='frequencia')),
    path('cadastro/', include('apps.cadastro.urls', namespace='cadastro')),
    path('tinymce/', include('tinymce.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.erros.views.error_404'
handler500 = 'apps.erros.views.error_500'
handler403 = 'apps.erros.views.error_403'
handler400 = 'apps.erros.views.error_400'
