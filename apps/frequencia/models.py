from django.db import models
from ..aluno.models import Aluno
from ..funcionario.models import Professor
from ..sala.models import Sala


class Frequencia(models.Model):
    sala = models.ForeignKey(Sala, related_name='freq_sala', on_delete=models.CASCADE)
    presentes = models.IntegerField(verbose_name='Presentes')
    data = models.DateField()
    status = models.BooleanField(verbose_name='Status', default=False)

    def __str__(self):
        return f'{self.sala} - {self.data}'


class FrequenciaAluno(models.Model):
    aluno = models.ForeignKey(Aluno, related_name='freq_aluno', on_delete=models.CASCADE)
    observacao = models.CharField(verbose_name='Observacao', null=True, blank=True, max_length=255)
    data = models.DateField()
    presente = models.BooleanField(verbose_name='Status', default=True)

    def __str__(self):
        return f'{self.aluno} - {self.data}'


class Registro(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, verbose_name='Sala')
    data = models.DateField(verbose_name='Semana Inicio')
    data_fim = models.DateField(verbose_name='Semana Final', null=True, blank=True)
    pratica = models.TextField(verbose_name='PRÁTICAS QUE POSSIBILITAM:')
    campo = models.TextField(verbose_name='CAMPOS DE EXPERIÊNCIAS:')
    objeto = models.TextField(verbose_name='OBJETOS DE APRENDIZAGEM:')
    professor = models.ForeignKey(Professor, verbose_name='Professor', null=True, blank=True, on_delete=models.SET_NULL)


class Periodo(models.Model):
    periodo = models.CharField(verbose_name='Período', max_length=100)


    def __str__(self):
        return self.periodo


class Relatorio(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.DO_NOTHING)
    aluno = models.ForeignKey(Aluno, on_delete=models.DO_NOTHING, related_name='relatorio_aluno')
    relatorio = models.TextField(verbose_name='Relatório')
    professor = models.ForeignKey(Professor, null=True, blank=True, on_delete=models.SET_NULL)
    data_relatorio = models.DateTimeField(auto_now_add=True)
    atualiza_relatorio = models.DateTimeField(auto_now=True)

