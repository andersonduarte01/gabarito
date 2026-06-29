from django.db import models


class TipoNotificacao(models.TextChoices):
    ACADEMICA  = 'ACADEMICA',  'Acadêmica'
    FINANCEIRA = 'FINANCEIRA', 'Financeira'
    COMUNICADO = 'COMUNICADO', 'Comunicado'
    SISTEMA    = 'SISTEMA',    'Sistema'


class Notificacao(models.Model):
    destinatario = models.ForeignKey(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name='Destinatário',
    )
    titulo    = models.CharField('Título', max_length=200)
    mensagem  = models.TextField('Mensagem')
    tipo      = models.CharField('Tipo', max_length=20, choices=TipoNotificacao.choices)
    lida      = models.BooleanField('Lida', default=False)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name        = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering            = ['-criado_em']

    def __str__(self):
        status = 'lida' if self.lida else 'não lida'
        return f'{self.destinatario.nome} — {self.titulo} ({status})'
