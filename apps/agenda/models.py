from django.db import models


class TipoEvento(models.TextChoices):
    REUNIAO     = 'REUNIAO',     'Reunião'
    PROVA       = 'PROVA',       'Prova / Avaliação'
    EXCURSAO    = 'EXCURSAO',    'Excursão'
    FESTIVIDADE = 'FESTIVIDADE', 'Festividade'
    OUTRO       = 'OUTRO',       'Outro'


class DestinatarioEvento(models.TextChoices):
    TODOS        = 'TODOS',        'Todos da escola'
    TURMAS       = 'TURMAS',       'Turmas específicas'
    RESPONSAVEIS = 'RESPONSAVEIS', 'Responsáveis'
    ALUNOS       = 'ALUNOS',       'Alunos'


class Evento(models.Model):
    escola        = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='eventos',
        verbose_name='Escola',
    )
    autor         = models.ForeignKey(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_criados',
        verbose_name='Autor',
    )
    titulo        = models.CharField('Título', max_length=200)
    descricao     = models.TextField('Descrição', blank=True)
    tipo          = models.CharField(
        'Tipo', max_length=20,
        choices=TipoEvento.choices,
        default=TipoEvento.OUTRO,
    )
    data_inicio   = models.DateField('Data de início')
    hora_inicio   = models.TimeField('Hora de início', null=True, blank=True)
    data_fim      = models.DateField('Data de término', null=True, blank=True)
    hora_fim      = models.TimeField('Hora de término', null=True, blank=True)
    local         = models.CharField('Local', max_length=200, blank=True)
    destinatarios = models.CharField(
        'Destinatários', max_length=20,
        choices=DestinatarioEvento.choices,
        default=DestinatarioEvento.TODOS,
    )
    turmas        = models.ManyToManyField(
        'turma.Turma',
        blank=True,
        related_name='eventos',
        verbose_name='Turmas',
    )
    publicada     = models.BooleanField('Publicado', default=False)
    criado_em     = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering            = ['data_inicio']

    def __str__(self):
        return self.titulo


class LeituraEvento(models.Model):
    evento  = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='leituras',
        verbose_name='Evento',
    )
    usuario = models.ForeignKey(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='leituras_evento',
        verbose_name='Usuário',
    )
    lido_em = models.DateTimeField('Lido em', auto_now_add=True)

    class Meta:
        verbose_name        = 'Leitura de Evento'
        verbose_name_plural = 'Leituras de Eventos'
        unique_together     = ('evento', 'usuario')

    def __str__(self):
        return f'{self.usuario} viu "{self.evento}"'
