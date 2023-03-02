
from django.db import models

# Create your models here.
from ..escola.models import UnidadeEscolar

ANO = [
    ('Selecione o ano', 'Selecione o ano'),
    ('Educação Infantil', 'Educação Infantil'),
    ('Pré-Escola', 'Pré-Escola'),
    ('1º Ano', '1° Ano'),
    ('2º Ano', '2° Ano'),
    ('3º Ano', '3° Ano'),
    ('4º Ano', '4° Ano'),
    ('5º Ano', '5° Ano'),
    ('6º Ano', '6° Ano'),
    ('7º Ano', '7° Ano'),
    ('8º Ano', '8° Ano'),
    ('9º Ano', '9° Ano'),
]

TURNO = [
    ('selecione', 'Selecione o turno'),
    ('manha', 'Manhã'),
    ('tarde', 'Tarde'),
    ('integral', 'Tempo Integral'),
]


class Ano(models.Model):
    descricao = models.CharField(verbose_name='Ano', choices=ANO, default='Selecione o ano', max_length=100)

    def __str__(self):
        return self.descricao


class Sala(models.Model):
    descricao = models.CharField(verbose_name='Sala', max_length=255)
    escola = models.ForeignKey(UnidadeEscolar, on_delete=models.CASCADE)
    turno = models.CharField(max_length=30, choices=TURNO, default='selecione')
    ano = models.ForeignKey(Ano, on_delete=models.DO_NOTHING, null=True, blank=True)
    total_alunos = models.IntegerField(verbose_name='Total Alunos', default=0)

    def __str__(self):
        return self.descricao


