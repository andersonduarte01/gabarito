from django.db import models


class AcaoAuditoria(models.TextChoices):
    CRIAR     = 'CRIAR',     'Criar'
    EDITAR    = 'EDITAR',    'Editar'
    DESATIVAR = 'DESATIVAR', 'Desativar'
    REATIVAR  = 'REATIVAR',  'Reativar'
    LOGIN     = 'LOGIN',     'Login'
    LOGOUT    = 'LOGOUT',    'Logout'


class LogAuditoria(models.Model):
    usuario   = models.ForeignKey(
        'core.Usuario',
        null=True,
        on_delete=models.SET_NULL,
        related_name='logs_auditoria',
        verbose_name='Usuário',
    )
    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        null=True,
        on_delete=models.SET_NULL,
        related_name='logs_auditoria',
        verbose_name='Escola',
    )
    papel_tipo = models.CharField('Papel', max_length=20, blank=True)
    acao       = models.CharField('Ação', max_length=20, choices=AcaoAuditoria.choices)
    modelo     = models.CharField('Modelo', max_length=100)
    objeto_id  = models.CharField('ID do Objeto', max_length=50)
    descricao  = models.TextField('Descrição')
    ip         = models.CharField('IP', max_length=45, blank=True)
    criado_em  = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name        = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering            = ['-criado_em']

    def __str__(self):
        return f'{self.get_acao_display()} {self.modelo} #{self.objeto_id} — {self.criado_em:%d/%m/%Y %H:%M}'
