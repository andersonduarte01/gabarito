from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from ..mobile.models import Chamada, MobileUsuario
from ..mobile.serializers import ChamadaSerializer



# API para o usuário solicitante
class ChamadaUsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = ChamadaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chamada.objects.filter(mobileusuario__email=user.email)

    def perform_create(self, serializer):
        mobile_user = MobileUsuario.objects.get(email=self.request.user.email)
        serializer.save(mobileusuario=mobile_user)


# API para o técnico
class ChamadaTecnicoViewSet(viewsets.ModelViewSet):
    serializer_class = ChamadaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chamada.objects.all()

    def perform_update(self, serializer):
        # Técnico só pode alterar o status
        serializer.save()
