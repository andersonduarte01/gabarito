from django.db import models

# Create your models here.
from apps.escola.models import UnidadeEscolar


class Funcao(models.Model):
    funcao = models.CharField(max_length=200, verbose_name='Funcao')
    codigo = models.CharField(max_length=200, verbose_name='Codigo')
    escola = models.ForeignKey(UnidadeEscolar, on_delete=models.CASCADE)

    def __str__(self):
        return self.funcao

    class Meta:
        verbose_name = 'Função'
        verbose_name_plural = 'Funções'



