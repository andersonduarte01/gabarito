from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditor_views
from rest_framework.routers import DefaultRouter
from apps.mobile.views import ChamadaTecnicoViewSet, ChamadaUsuarioViewSet, ChamadaFinalizadaTecnicoViewSet
from apps.mobile.views import MobileUsuarioViewSet, MobileTecnicoViewSet, ChamadaFinalizadaUsuarioViewSet
from apps.mobile.views import ChamadaAguardandoUsuarioViewSet, ChamadaAguardandoTecnicoViewSet


from apps.mobile.views import MyTokenObtainPairView


router_usuario = DefaultRouter()
router_usuario.register(r'chamados-usuario', ChamadaUsuarioViewSet, basename='chamados-usuario')
router_usuario.register(r'usuarios', MobileUsuarioViewSet, basename='usuarios')
router_usuario.register(r'chamados-usuario-finalizados', ChamadaFinalizadaUsuarioViewSet, basename='chamados-usuario-finalizados')
router_usuario.register(r'chamados-usuario-aguardando', ChamadaAguardandoUsuarioViewSet, basename='chamados-usuario-aguardando')


router_tecnico = DefaultRouter()
router_tecnico.register(r'chamados-tecnico', ChamadaTecnicoViewSet, basename='chamados-tecnico')
router_tecnico.register(r'tecnicos', MobileTecnicoViewSet, basename='tecnicos')
router_tecnico.register(r'chamados-finalizados', ChamadaFinalizadaTecnicoViewSet, basename='chamados-finalizados')
router_tecnico.register(r'chamados-tecnico-aguardando', ChamadaAguardandoTecnicoViewSet, basename='chamados-tecnico-aguardando')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('apps.core.urls', namespace='core')),
    path('escola/', include('apps.escola.urls', namespace='escola')),
    path('professor/', include('apps.funcionario.urls', namespace='funcionario')),
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
    path('ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(login_required(ckeditor_views.browse)), name='ckeditor_browse'),
    path('api/v1/', include(router_usuario.urls)),
    path('api/v1/', include(router_tecnico.urls)),
    path('api/', include('apps.mobile.urls')),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.erros.views.error_404'
handler500 = 'apps.erros.views.error_500'
handler403 = 'apps.erros.views.error_403'
handler400 = 'apps.erros.views.error_400'
