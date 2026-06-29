import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


class CanalConvite(models.TextChoices):
    EMAIL    = 'EMAIL',    'E-mail'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'


class ConviteOnboarding(models.Model):
    escola      = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='convites',
        verbose_name='Escola',
    )
    email       = models.EmailField('E-mail do Diretor')
    telefone    = models.CharField('Telefone', max_length=20, blank=True)
    token       = models.UUIDField('Token', default=uuid.uuid4, unique=True, editable=False)
    canal_envio = models.CharField(
        'Canal de Envio',
        max_length=10,
        choices=CanalConvite.choices,
        default=CanalConvite.EMAIL,
    )
    usado       = models.BooleanField('Usado', default=False)
    criado_em   = models.DateTimeField('Criado em', auto_now_add=True)
    expira_em   = models.DateTimeField('Expira em')

    class Meta:
        verbose_name        = 'Convite de Onboarding'
        verbose_name_plural = 'Convites de Onboarding'
        ordering            = ['-criado_em']

    def __str__(self):
        return f'Convite para {self.escola} ({self.email})'

    def save(self, *args, **kwargs):
        if not self.pk and not self.expira_em:
            self.expira_em = timezone.now() + timedelta(hours=72)
        super().save(*args, **kwargs)

    @property
    def valido(self) -> bool:
        return not self.usado and timezone.now() <= self.expira_em
