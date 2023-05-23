from enum import unique

from django.db import models
from django.urls import reverse

from ..perfil.models import Pessoa, Endereco
from ..sala.models import Sala


PORT_DEF = [
    ('nao', 'Não'),
    ('TDAH', 'TDAH - Transtorno de déficit de atenção com hiperatividade'),
    ('TEA', 'TEA - Transtorno do espectro autista'),
    ('TOD', 'TOD - Transtorno opositivo desafiador'),
    ('TDL', 'TDL - Transtorno do desenvolvimento da linguagem'),
]

SITUACAO = [
    ('1', 'Matriculado(a)'),
    ('2', 'Transferido(a)'),
    ('3', 'Outro'),
]

SEXO = [
    ('M', 'Masculino'),
    ('F', 'Feminino'),
    ('O', 'Outro'),
]


class Aluno(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)
    data_nascimento = models.CharField(max_length=20, verbose_name='Data de Nascimento', null=True, blank=True, help_text='dia/mes/ano')
    sexo = models.CharField(verbose_name='Sexo', choices=SEXO, default='Outro', max_length=100)
    portador_deficiencia = models.CharField(verbose_name='Portador de deficiência?', choices=PORT_DEF, default='nao', max_length=255)
    responsavel_legal = models.CharField(verbose_name='Responsável Legal', max_length=120)
    situacao = models.CharField(verbose_name='Situação', max_length=120, choices=SITUACAO, default='1')
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
