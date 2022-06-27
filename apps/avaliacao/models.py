from enum import unique

from django.db import models

from apps.aluno.models import Aluno
from apps.sala.models import Ano


class Avaliacao(models.Model):
    descricao = models.CharField(max_length=255, verbose_name='Descrição')
    ano = models.ForeignKey(Ano, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'



RESPOSTA = [
    ('0', 'Selecione a resposta correta'),
    ('1', '01'),
    ('2', '02'),
    ('3', '03'),
    ('4', '04'),
]


class Questao(models.Model):
    numero = models.CharField(verbose_name='Número', max_length=3)
    texto = models.TextField(null=True, blank=True)
    questao = models.TextField()
    opcao_um = models.CharField(max_length=255, verbose_name='01')
    opcao_dois = models.CharField(max_length=255, verbose_name='02')
    opcao_tres = models.CharField(max_length=255, verbose_name='03')
    opcao_quatro = models.CharField(max_length=255, verbose_name='04')
    opcao_certa = models.CharField(verbose_name='Resposta certa', choices=RESPOSTA, default='0', max_length=12)
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.numero

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'


class Gabarito(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.DO_NOTHING)
    qtd_acertos = models.IntegerField(verbose_name='Acertos', default=0)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return self.avaliacao.descricao

    class Meta:
        verbose_name = 'Gabarito'
        verbose_name_plural = 'Gabaritos'


class Resposta(models.Model):
    resposta = models.CharField(verbose_name='Resposta', max_length=6, default='')
    gabarito = models.ForeignKey(Gabarito, on_delete=models.CASCADE)
    questao = models.ForeignKey(Questao, on_delete=models.DO_NOTHING)
    acertou = models.BooleanField(default=False)

    def __str__(self):
        return self.resposta