from rest_framework import serializers

from .models import UnidadeEscolar, EnderecoEscolar, AnoLetivo


class EnderecoEscolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnderecoEscolar
        fields = ('rua', 'numero', 'complemento', 'bairro', 'cep', 'cidade', 'estado')


class AnoLetivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnoLetivo
        fields = ('ano', 'inicio', 'fim', 'corrente')


class UnidadeEscolarSerializer(serializers.ModelSerializer):
    endereco = serializers.SerializerMethodField()
    ano_letivo_corrente = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = UnidadeEscolar
        fields = (
            'id',
            'nome_escola',
            'tipo',
            'tipo_display',
            'email',
            'telefone',
            'logo_escola',
            'inep',
            'cnpj',
            'site',
            'ativo',
            'endereco',
            'ano_letivo_corrente',
        )

    def get_endereco(self, obj):
        try:
            return EnderecoEscolarSerializer(obj.endereco_obj).data
        except EnderecoEscolar.DoesNotExist:
            return None

    def get_ano_letivo_corrente(self, obj):
        ano = obj.anos_letivos.filter(corrente=True).first()
        if ano:
            return AnoLetivoSerializer(ano).data
        return None


class UnidadeEscolarSerializerEdit(serializers.ModelSerializer):
    class Meta:
        model = UnidadeEscolar
        fields = ('nome_escola', 'tipo', 'email', 'telefone', 'inep', 'cnpj', 'site')

    def validate_cnpj(self, value):
        from apps.core.validators import normalizar_cnpj, validate_cnpj
        cnpj = normalizar_cnpj(value)
        if cnpj:
            validate_cnpj(cnpj)
        return cnpj

    def validate_telefone(self, value):
        from apps.core.validators import normalizar_telefone, validate_telefone
        telefone = normalizar_telefone(value)
        if telefone:
            validate_telefone(telefone)
        return telefone
