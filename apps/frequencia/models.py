from django.db import models
from ..aluno.models import Aluno
from ..sala.models import Sala


# Create your models here.


class Frequencia(models.Model):
    sala = models.ForeignKey(Sala, related_name='freq_sala', on_delete=models.DO_NOTHING)
    presentes = models.IntegerField(verbose_name='Presentes')
    data = models.DateField()
    status = models.BooleanField(verbose_name='Status', default=False)

    def __str__(self):
        return f'{self.sala} - {self.data}'


class FrequenciaAluno(models.Model):
    aluno = models.ForeignKey(Aluno, related_name='freq_aluno', on_delete=models.CASCADE)
    observacao = models.TextField(verbose_name='Observacao', null=True, blank=True)
    data = models.DateField()
    presente = models.BooleanField(verbose_name='Status', default=True)

    def __str__(self):
        return f'{self.aluno} - {self.data}'


