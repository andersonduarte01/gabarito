from rest_framework import viewsets, permissions, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from ..core.models import Usuario
from ..mobile.models import Chamada, MobileUsuario, MobileTecnico
from ..mobile.serializers import ChamadaSerializer, MobileTecnicoSerializer, MobileUsuarioSerializer, \
    ChamadaStatusUpdateSerializer, MyTokenObtainPairSerializer, UsuarioSerializer, UsuarioCreateSerializer, \
    MobileUsuarioResumoSerializer


class MobileTecnicoViewSet(viewsets.ModelViewSet):
    queryset = MobileTecnico.objects.all()
    serializer_class = MobileTecnicoSerializer
    permission_classes = [IsAuthenticated]


class MobileUsuarioViewSet(viewsets.ModelViewSet):
    queryset = MobileUsuario.objects.all()
    serializer_class = MobileUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'mobiletecnico'):
            raise PermissionDenied('Apenas técnicos podem cadastrar usuários.')

        serializer.save(tecnico=user.mobiletecnico, is_solicitante=True)


class ChamadaUsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = ChamadaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chamada.objects.filter(mobileusuario__email=user.email)

    def perform_create(self, serializer):
        mobile_user = MobileUsuario.objects.get(email=self.request.user.email)
        serializer.save(mobileusuario=mobile_user)


class ChamadaTecnicoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chamada.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ChamadaStatusUpdateSerializer
        return ChamadaSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UsuarioLogadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Verifica se é Técnico
        is_tecnico = MobileTecnico.objects.filter(id=user.id).exists()

        # Verifica se é Solicitante (usuário comum)
        mobile_usuario = MobileUsuario.objects.filter(id=user.id).first()

        is_solicitante = bool(mobile_usuario) and mobile_usuario.is_solicitante
        escola_id = mobile_usuario.escola.id if mobile_usuario and mobile_usuario.escola else None
        escola_nome = mobile_usuario.escola.nome if mobile_usuario and mobile_usuario.escola else None

        return Response({
            'id': user.id,
            'email': user.email,
            'nome': user.nome,
            'is_tecnico': is_tecnico,
            'is_solicitante': is_solicitante,
            'is_professor': user.is_professor,
            'is_administrator': user.is_administrator,
            'is_funcionario': user.is_funcionario,
            'is_aluno': user.is_aluno,
            'is_active': user.is_active,
            'escola_id': escola_id,
            'escola_nome': escola_nome,
        })


class UsuarioCreateView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioCreateSerializer


class ChamadaFinalizadaTecnicoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChamadaSerializer

    def get_queryset(self):
        # Pega o técnico logado
        tecnico_logado = getattr(self.request.user, 'mobiletecnico', None)
        if not tecnico_logado:
            return Chamada.objects.none()  # Se não for técnico, retorna queryset vazio

        # Filtra chamados finalizados/cancelados dos usuários vinculados ao técnico logado
        return Chamada.objects.filter(
            status_chamado__in=['2', '3'],
            mobileusuario__tecnico=tecnico_logado
        ).order_by('data')

class ChamadaFinalizadaUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChamadaSerializer

    def get_queryset(self):
        user = self.request.user
        return Chamada.objects.filter(mobileusuario=user, status_chamado__in=['2', '3']).order_by('data')


class ChamadaAguardandoUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChamadaSerializer

    def get_queryset(self):
        return Chamada.objects.filter(
            mobileusuario=self.request.user,
            status_chamado='1'
        ).order_by('data')


class ChamadaAguardandoTecnicoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChamadaSerializer

    def get_queryset(self):
        user = self.request.user
        # Filtra apenas os chamados cujo usuário vinculado tem o tecnico igual ao logado
        return Chamada.objects.filter(
            status_chamado='1',
            mobileusuario__tecnico=user
        ).order_by('data')


class ChamadaAguardandoDoSolicitanteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChamadaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Pega o MobileUsuario correspondente ao usuário logado
        usuario_logado = MobileUsuario.objects.get(id=self.request.user.id)

        # Se o usuário não tiver técnico vinculado, retorna queryset vazio
        if not usuario_logado.tecnico:
            return Chamada.objects.none()

        # Retorna todas as chamadas aguardando do técnico vinculado
        return Chamada.objects.filter(
            status_chamado='1',
            mobileusuario__tecnico=usuario_logado.tecnico
        ).order_by('data')


class UsuariosDoTecnicoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MobileUsuarioResumoSerializer

    def get_queryset(self):
        # Pega o técnico logado
        tecnico_logado = getattr(self.request.user, 'mobiletecnico', None)
        if not tecnico_logado:
            return MobileUsuario.objects.none()

        # Retorna apenas os usuários vinculados ao técnico logado
        return MobileUsuario.objects.filter(tecnico=tecnico_logado).order_by('nome')