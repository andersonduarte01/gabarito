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


FALTA = [
    ('0', 'Selecione uma opção'),
    ('1', 'Ausência justificada'),
    ('2', 'Ausência não justificada'),
]


class FrequenciaAluno(models.Model):
    aluno = models.ForeignKey(Aluno, related_name='freq_aluno', on_delete=models.CASCADE)
    observacao = models.CharField(verbose_name='Observacao', null=True, blank=True, max_length=255)
    data = models.DateField()
    presente = models.BooleanField(verbose_name='Status', default=True)
    falta_justificada = models.CharField(verbose_name='Falta Justificada', default='0', choices=FALTA, max_length=155)

    def __str__(self):
        return f'{self.aluno} - {self.data}'

