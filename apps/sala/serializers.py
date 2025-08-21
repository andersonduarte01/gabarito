from rest_framework import serializers
from .models import Sala, Ano
from ..aluno.models import Aluno


class SalaSerializer(serializers.ModelSerializer):
    escola_nome = serializers.CharField(source='escola.nome_escola', read_only=True)
    ano_descricao = serializers.CharField(source='ano.descricao', read_only=True)

    class Meta:
        model = Sala
        fields = [
            'id',
            'descricao',
            'escola',
            'escola_nome',
            'turno',
            'ano',
            'ano_descricao',
            'total_alunos',
            'ano_letivo',
        ]
        read_only_fields = [
            'escola',         # <- não pode vir do frontend
            'ano_letivo',     # <- não pode vir do frontend
            'total_alunos',
            'ano_descricao',
        ]


class SalaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = ['descricao', 'turno', 'ano']


class AnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ano
        fields = ['id', 'descricao']


class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'data_nascimento', 'sexo']


class ProfessorSalasSerializer(serializers.ModelSerializer):
    escola_nome = serializers.CharField(source='escola.nome_escola', read_only=True)
    ano_descricao = serializers.CharField(source='ano.descricao', read_only=True)

    class Meta:
        model = Sala
        fields = [
            'id',
            'descricao',
            'escola',
            'escola_nome',
            'turno',
            'ano',
            'ano_descricao',
            'total_alunos',
            'ano_letivo',
        ]
        read_only_fields = [
            'escola',         # <- não pode vir do frontend
            'ano_letivo',     # <- não pode vir do frontend
            'total_alunos',
            'ano_descricao',
        ]

