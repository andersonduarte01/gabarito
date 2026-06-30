from django.db import models


class TipoComunicado(models.TextChoices):
    GERAL       = 'GERAL',       'Geral'
    CONVOCACAO  = 'CONVOCACAO',  'Convocação'
    AVISO       = 'AVISO',       'Aviso'
    ADVERTENCIA = 'ADVERTENCIA', 'Advertência'
    ELOGIO      = 'ELOGIO',      'Elogio'
    OUTRO       = 'OUTRO',       'Outro'


class DestinatarioComunicado(models.TextChoices):
    TODOS        = 'TODOS',        'Todos da escola'
    TURMAS       = 'TURMAS',       'Turmas específicas'
    RESPONSAVEIS = 'RESPONSAVEIS', 'Responsáveis'
    ALUNOS       = 'ALUNOS',       'Alunos'


class Comunicado(models.Model):
    escola        = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='comunicados',
        verbose_name='Escola',
    )
    autor         = models.ForeignKey(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='comunicados_enviados',
        verbose_name='Autor',
    )
    titulo        = models.CharField('Título', max_length=200)
    corpo         = models.TextField('Conteúdo')
    tipo          = models.CharField(
        'Tipo', max_length=20,
        choices=TipoComunicado.choices,
        default=TipoComunicado.GERAL,
    )
    destinatarios = models.CharField(
        'Destinatários', max_length=20,
        choices=DestinatarioComunicado.choices,
        default=DestinatarioComunicado.TODOS,
    )
    turmas        = models.ManyToManyField(
        'turma.Turma',
        blank=True,
        related_name='comunicados',
        verbose_name='Turmas',
    )
    publicada     = models.BooleanField('Publicado', default=False)
    criado_em     = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Comunicado'
        verbose_name_plural = 'Comunicados'
        ordering            = ['-criado_em']

    def __str__(self):
        return self.titulo


class LeituraComunicado(models.Model):
    comunicado = models.ForeignKey(
        Comunicado,
        on_delete=models.CASCADE,
        related_name='leituras',
        verbose_name='Comunicado',
    )
    usuario    = models.ForeignKey(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='leituras_comunicado',
        verbose_name='Usuário',
    )
    lido_em    = models.DateTimeField('Lido em', auto_now_add=True)

    class Meta:
        verbose_name        = 'Leitura de Comunicado'
        verbose_name_plural = 'Leituras de Comunicados'
        unique_together     = ('comunicado', 'usuario')

    def __str__(self):
        return f'{self.usuario} leu "{self.comunicado}"'
