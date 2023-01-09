from django.db import models

from ..sala.models import Sala


# Create your models here.


class Frequencia(models.Model):
    sala = models.ForeignKey(Sala, related_name='freq_sala', on_delete=models.DO_NOTHING)
    presentes = models.IntegerField(verbose_name='Presentes')
    total = models.IntegerField(verbose_name='Total')
    observacao = models.TextField(verbose_name='Observacao', null=True, blank=True)
    data = models.DateField()
    status = models.BooleanField(verbose_name='Status', default=False)

    def __str__(self):
        return f'{self.sala} - {self.data}'

