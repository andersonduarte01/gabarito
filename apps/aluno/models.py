from enum import unique

from django.db import models
from django.urls import reverse

from ..sala.models import Sala


class Aluno(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)
    sala = models.ForeignKey(Sala, verbose_name='Sala', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name='Aluno'
        verbose_name_plural = 'Alunos'
