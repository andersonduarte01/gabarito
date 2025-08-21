from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'salas'

router = DefaultRouter()
router.register(r'salas', views.SalaViewSet, basename='sala')
router1 = DefaultRouter()
router1.register(r'anos', views.AnoViewSet, basename='ano')
router2 = DefaultRouter()
router2.register(r'alunos/(?P<sala_pk>\d+)', views.AlunoViewSet, basename='aluno')
router3 = DefaultRouter()
router3.register(r'professores', views.ProfessorSalasViewSet, basename='professor')


urlpatterns = [
    path('adicionar_sala/', views.AdicionarSala.as_view(), name='adicionar_sala'),
    path('editar_sala/<int:pk>/', views.EditarSala.as_view(), name='edit_sala'),
    path('<int:pk>/deletar/', views.DeletarSala.as_view(), name='deletar_sala'),
    #### API ###
    path('api/', include(router.urls)),
    path('anos/', include(router1.urls)),
    path('api/edit_del_sala/<int:pk>/',
         views.EditarExcluirSala.as_view(),
         name='editar_excluir_sala'),
    path('alunos_api/', include(router2.urls)),
    path('professor_api/', include(router3.urls)),

]
