from django.db import models
from stdimage import StdImageField

from ..core.models import Usuario


class UnidadeEscolar(Usuario):
    nome_escola = models.CharField(verbose_name='Escola', max_length=200)
    slug = models.SlugField(max_length=200)
    logo_escola = StdImageField(upload_to='Imagens/Logo',
                                variations={'thumbnail': {'width': 716, 'height': 716}},
                                null=True, blank=True,
                                delete_orphans=True)
    inep = models.CharField(verbose_name='INEP', max_length=20, null=True, blank=True)
    cnpj = models.CharField(verbose_name='CNPJ', max_length=25, null=True, blank=True)
    telefone = models.CharField(verbose_name='Telefone', max_length=20)

    def __str__(self):
        return self.nome_escola

    def imagem(self):
        if self.logo_escola:
            return True
        else:
            return False

    class Meta:
        verbose_name = 'Escola'
        verbose_name_plural = 'Escolas'


class EnderecoEscolar(models.Model):
    endereco = models.ForeignKey(UnidadeEscolar, on_delete=models.CASCADE)
    rua = models.CharField(verbose_name='Rua', max_length=100)
    numero = models.CharField(verbose_name='Número', max_length=20)
    complemento = models.CharField(verbose_name='Complemento', max_length=200)
    bairro = models.CharField(verbose_name='Bairro', max_length=100)
    cep = models.CharField(verbose_name='Cep', max_length=10)
    cidade = models.CharField(verbose_name='Cidade', max_length=100)
    estado = models.CharField(verbose_name='Estado', max_length=30)

    def __str__(self):
        return f"Escola {self.endereco.nome_escola}"

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereço'


class AnoLetivo(models.Model):
    ano = models.IntegerField(verbose_name='Ano Letivo', unique=True)
    inicio = models.DateField(verbose_name='Início do Ano Letivo')
    fim = models.DateField(verbose_name='Fim do Ano Letivo')
    corrente = models.BooleanField(verbose_name='Ano Corrente', default=False)  # Indica se é o ano letivo atual
    descricao = models.TextField(verbose_name='Descrição', blank=True, null=True)

    def __str__(self):
        return f'Ano Letivo {self.ano}'

    def save(self, *args, **kwargs):
        # Garante que apenas um Ano Letivo seja marcado como corrente
        if self.corrente:
            AnoLetivo.objects.filter(corrente=True).update(corrente=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Ano Letivo'
        verbose_name_plural = 'Anos Letivos'

