from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..core.models import Usuario
from ..mobile.models import MobileUsuario, MobileTecnico, Chamada


class MobileUsuarioResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileUsuario
        fields = ['id', 'nome', 'email']


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nome']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nome', 'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class MobileTecnicoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MobileTecnico
        fields = ['id', 'email', 'nome', 'password', 'is_tecnico']

    def create(self, validated_data):
        validated_data['is_tecnico'] = True  # Garante que seja técnico
        password = validated_data.pop('password')
        tecnico = super().create(validated_data)
        tecnico.set_password(password)
        tecnico.save()
        return tecnico


class MobileUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MobileUsuario
        fields = ['id', 'email', 'nome', 'password', 'escola', 'is_solicitante']
        read_only_fields = ['is_solicitante']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request.user, 'mobiletecnico'):
            raise serializers.ValidationError('Apenas técnicos podem criar usuários.')

        validated_data['is_solicitante'] = True
        validated_data['tecnico'] = request.user.mobiletecnico

        password = validated_data.pop('password')
        usuario = super().create(validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class ChamadaStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chamada
        fields = ['status_chamado']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['nome'] = user.nome
        return token

    def validate(self, attrs):
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }

        user = authenticate(**credentials)

        if user is None or not user.is_active:
            raise serializers.ValidationError('Email ou senha incorretos')

        data = super().validate(attrs)
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'nome': user.nome,
        }
        return data


class ChamadaSerializer(serializers.ModelSerializer):
    mobileusuario = MobileUsuarioResumoSerializer(read_only=True)
    class Meta:
        model = Chamada
        fields = '__all__'
