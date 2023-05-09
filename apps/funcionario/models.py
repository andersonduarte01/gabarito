from django.db import models

from ..core.models import Usuario
from ..escola.models import UnidadeEscolar
from ..funcao.models import Funcao
from ..perfil.models import Pessoa, Endereco


class Funcionario(Usuario):
    escola = models.ForeignKey(UnidadeEscolar, on_delete=models.CASCADE)
    perfil = models.OneToOneField(Pessoa, on_delete=models.CASCADE, null=True, blank=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, verbose_name='Endereço', null=True, blank=True)
    funcao = models.ForeignKey(Funcao, on_delete=models.SET_NULL, verbose_name='Função', null=True, blank=True)

    def __str__(self):
        return self.escola.nome

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'


class Professor(Usuario):
    professor_nome = models.CharField(verbose_name='Professor', max_length=255)
    escola = models.ForeignKey(UnidadeEscolar, on_delete=models.CASCADE)
    perfil = models.OneToOneField(Pessoa, on_delete=models.CASCADE, null=True, blank=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, verbose_name='Endereço', null=True, blank=True)

    def __str__(self):
        return self.professor_nome

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'

