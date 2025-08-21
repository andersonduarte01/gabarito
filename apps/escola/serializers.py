from rest_framework import serializers
from .models import UnidadeEscolar, EnderecoEscolar

class EnderecoEscolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnderecoEscolar
        fields = ['rua', 'numero', 'complemento', 'bairro', 'cep', 'cidade', 'estado']

class UnidadeEscolarSerializer(serializers.ModelSerializer):
    endereco = serializers.SerializerMethodField()

    class Meta:
        model = UnidadeEscolar
        fields = ['nome_escola', 'email', 'logo_escola', 'inep', 'cnpj', 'telefone', 'endereco']

    def get_endereco(self, obj):
        endereco = EnderecoEscolar.objects.filter(endereco=obj).first()
        if endereco:
            return EnderecoEscolarSerializer(endereco).data
        return None

class UnidadeEscolarSerializerEdit(serializers.ModelSerializer):
    class Meta:
        model = UnidadeEscolar
        fields = [ 'email', 'inep', 'cnpj', 'telefone']
