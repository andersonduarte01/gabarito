from rest_framework import serializers
from ..core.models import Usuario
from ..mobile.models import MobileUsuario
from ..mobile.models import Chamada


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nome', 'is_funcionario', 'is_administrator',
                  'is_professor', 'is_tecnico', 'is_solicitante', 'is_aluno',
                  'is_admin', 'cadastrado_em', 'atualizado_em']


class MobileUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileUsuario
        fields = ['id', 'email', 'nome', 'escola']


class ChamadaSerializer(serializers.ModelSerializer):
    mobileusuario = MobileUsuarioSerializer(read_only=True)

    class Meta:
        model = Chamada
        fields = ['id', 'mobileusuario', 'manutencao', 'descricao', 'data',
                  'data_up', 'status_chamado']
