from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from ..core.models import Usuario
from ..escola.models import UnidadeEscolar
from ..funcionario.models import Professor

class ProfessorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Professor
        fields = ['id', 'professor_nome', 'email', 'password']

    def create(self, validated_data):
        request = self.context.get('request')
        escola = UnidadeEscolar.objects.get(id=request.user.id)

        professor = Professor.objects.create(
            email=validated_data.pop('email'),
            professor_nome=validated_data.pop('professor_nome'),
            password=make_password(validated_data.pop('password')),
            is_professor=True,
            escola=escola
        )

        # Agora atribui a escola
        professor.escola = escola
        professor.save()
        return professor

    def update(self, instance, validated_data):
        instance.professor_nome = validated_data.get('professor_nome', instance.professor_nome)
        if 'email' in validated_data:
            instance.email = validated_data['email']
        if 'password' in validated_data:
            instance.password = make_password(validated_data['password'])
        instance.save()
        return instance