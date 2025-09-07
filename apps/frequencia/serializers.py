from rest_framework import serializers
from .models import Frequencia, FrequenciaAluno, Registro, Relatorio, Periodo

class FrequenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frequencia
        fields = ['id', 'sala', 'presentes', 'data', 'status']


class FrequenciaAlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequenciaAluno
        fields = ['id', 'aluno', 'data', 'presente', 'observacao']


class FrequenciaAlunoBlocoSerializer(serializers.Serializer):
    aluno = serializers.IntegerField()
    presente = serializers.BooleanField()
    observacao = serializers.CharField(required=False, allow_blank=True)


class FrequenciaBlocoSerializer(serializers.Serializer):
    sala_id = serializers.IntegerField()
    data = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'])
    frequencias_alunos = FrequenciaAlunoBlocoSerializer(many=True)


class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = "__all__"


class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = "__all__"


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = ['id', 'periodo']
