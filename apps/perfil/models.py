from cpf_field.models import CPFField
from django.db import models

# Create your models here.
from stdimage import StdImageField


class Endereco(models.Model):
    rua = models.CharField(verbose_name='Rua', max_length=100)
    numero = models.CharField(verbose_name='Número', max_length=20)
    complemento = models.CharField(verbose_name='Complemento', max_length=200, blank=True, null=True)
    bairro = models.CharField(verbose_name='Bairro', max_length=100)
    cep = models.CharField(verbose_name='Cep', max_length=10, blank=True)
    cidade = models.CharField(verbose_name='Cidade', max_length=100, blank=True)
    estado = models.CharField(verbose_name='Estado', max_length=30, blank=True)

    def __str__(self):
        return self.rua

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'


class Pessoa(models.Model):
    foto = StdImageField(upload_to='Imagens/perfil',
                                variations={'thumbnail': {'width': 716, 'height': 716}},
                                null=True, blank=True,
                                delete_orphans=True)
    data_nascimento = models.DateTimeField(verbose_name='Data de Nascimento', null=True, blank=True)
    cpf = CPFField('CPF', blank=True, null=True)
    telefone = models.CharField(verbose_name='Telefone', max_length=20, null=True, blank=True)

    def __str__(self):
        return self.cpf

    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'

