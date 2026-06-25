from django.urls import path

from . import views

app_name = 'planos'

urlpatterns = [
    path('acesso-bloqueado/', views.AcessoBloqueadoView.as_view(), name='acesso_bloqueado'),

    # Planos (platform admin)
    path('',                  views.ListarPlanosView.as_view(),  name='listar_planos'),
    path('novo/',             views.CriarPlanoView.as_view(),    name='criar_plano'),
    path('<int:pk>/editar/',  views.EditarPlanoView.as_view(),   name='editar_plano'),

    # Assinaturas (platform admin)
    path('assinaturas/',                           views.ListarAssinaturasView.as_view(),    name='listar_assinaturas'),
    path('assinaturas/<int:pk>/',                  views.DetalheAssinaturaView.as_view(),    name='detalhe_assinatura'),
    path('assinaturas/<int:pk>/ativar/',           views.AtivarAssinaturaView.as_view(),     name='ativar_assinatura'),
    path('assinaturas/<int:pk>/grace/',            views.IniciarGraceView.as_view(),         name='iniciar_grace'),
    path('assinaturas/<int:pk>/suspender/',        views.SuspenderAssinaturaView.as_view(),  name='suspender_assinatura'),
    path('assinaturas/<int:pk>/cancelar/',         views.CancelarAssinaturaView.as_view(),   name='cancelar_assinatura'),
]
