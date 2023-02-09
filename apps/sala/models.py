
from django.db import models

# Create your models here.
from ..escola.models import UnidadeEscolar

ANO = [
    (0, 'Selecione o ano'),
    (1, '1° Ano'),
    (2, '2° Ano'),
    (3, '3° Ano'),
    (4, '4° Ano'),
    (5, '5° Ano'),
    (6, '6° Ano'),
    (7, '7° Ano'),
    (8, '8° Ano'),
    (9, '9° Ano'),
]

TURNO = [
    ('selecione', 'Selecione o turno'),
    ('manha', 'Manhã'),
    ('tarde', 'Tarde'),
    ('integral', 'Tempo Integral'),
]


class Ano(models.Model):
    descricao = models.IntegerField(verbose_name='Ano', choices=ANO, default=0)

    def __str__(self):
        return str(self.descricao)


class Sala(models.Model):
    descricao = models.CharField(verbose_name='Sala', max_length=255)
    escola = models.ForeignKey(UnidadeEscolar, on_delete=models.CASCADE)
    turno = models.CharField(max_length=30, choices=TURNO, default='selecione')
    ano = models.ForeignKey(Ano, on_delete=models.DO_NOTHING, null=True, blank=True)
    total_alunos = models.IntegerField(verbose_name='Total Alunos', default=0)

    def __str__(self):
        return self.descricao


