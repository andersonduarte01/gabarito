from enum import unique

from django.db import models
from django.urls import reverse

from ..perfil.models import Pessoa, Endereco
from ..sala.models import Sala


class Aluno(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)
    perfil = models.ForeignKey(Pessoa, verbose_name='Perfil', on_delete=models.CASCADE, blank=True, null=True)
    endereco = models.ForeignKey(Endereco, verbose_name='Endereço', on_delete=models.CASCADE, blank=True, null=True)
    sala = models.ForeignKey(Sala, verbose_name='Sala', on_delete=models.DO_NOTHING)

    def get_success_url(self):
            return reverse('salas:alunos', kwargs={'pk': self.get_context_data()['aluno'].sala.pk})

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name='Aluno'
        verbose_name_plural = 'Alunos'
