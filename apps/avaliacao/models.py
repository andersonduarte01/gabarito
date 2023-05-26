from django.conf import settings
from django.db import models
from stdimage import StdImageField

from ..aluno.models import Aluno
from ..escola.models import UnidadeEscolar
from ..sala.models import Ano


class Avaliacao(models.Model):
    descricao = models.CharField(max_length=255, verbose_name='Descrição')
    ano = models.ForeignKey(Ano, on_delete=models.DO_NOTHING)
    escola = models.ManyToManyField(UnidadeEscolar, related_name='avaliacao_escola')
    escola_responde = models.BooleanField(default=False, verbose_name='SME')
    data_encerramento = models.DateField(verbose_name='Encerramento')

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'


class Questao(models.Model):
    numero = models.CharField(verbose_name='Número', max_length=3, null=True, blank=True)
    texto = models.TextField(null=True, blank=True)
    imagem_prova = StdImageField(upload_to='Imagens/Logo',
                                variations={'thumbnail': {'width': 600, 'height': 450}},
                                null=True, blank=True,
                                delete_orphans=True, verbose_name='imagem')
    questao = models.TextField()
    opcao_um = models.CharField(max_length=255, verbose_name='01')
    opcao_dois = models.CharField(max_length=255, verbose_name='02')
    opcao_tres = models.CharField(max_length=255, verbose_name='03')
    opcao_quatro = models.CharField(max_length=255, verbose_name='04')
    RESPOSTA = [
        ('0', 'Selecione a resposta correta'),
        ('1', '01'),
        ('2', '02'),
        ('3', '03'),
        ('4', '04'),
    ]
    opcao_certa = models.CharField(verbose_name='Resposta certa', choices=RESPOSTA, default='0', max_length=12)
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.questao

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
    gabarito = models.ForeignKey(Gabarito, on_delete=models.CASCADE, null=True, blank=True)
    questao = models.ForeignKey(Questao, on_delete=models.DO_NOTHING)
    acertou = models.BooleanField(default=False)

    def corrigirQuestao(self):
        return self.questao.opcao_certa

    def marcada(self):
        return self.resposta


    def __str__(self):
        return self.resposta