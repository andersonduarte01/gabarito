from django.db import models

from apps.core.validators import validate_cpf, validate_telefone, normalizar_cpf, normalizar_telefone


class Colaborador(models.Model):
    usuario = models.OneToOneField(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='colaborador',
        verbose_name='Usuário',
    )
    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='colaboradores',
        verbose_name='Escola',
    )
    funcao = models.ForeignKey(
        'funcao.Funcao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='colaboradores',
        verbose_name='Função',
    )
    cpf = models.CharField(
        verbose_name='CPF',
        max_length=11,
        blank=True,
        validators=[validate_cpf],
    )
    telefone = models.CharField(
        verbose_name='Telefone',
        max_length=11,
        blank=True,
        validators=[validate_telefone],
    )
    foto = models.ImageField(
        verbose_name='Foto',
        upload_to='colaboradores/',
        null=True,
        blank=True,
    )
    ativo = models.BooleanField(verbose_name='Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'
        ordering = ['usuario__nome']

    def __str__(self):
        return self.usuario.nome

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = normalizar_cpf(self.cpf)
        if self.telefone:
            self.telefone = normalizar_telefone(self.telefone)
        super().save(*args, **kwargs)


class Professor(models.Model):
    usuario = models.OneToOneField(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='professor',
        verbose_name='Usuário',
    )
    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='professores',
        verbose_name='Escola',
    )
    cpf = models.CharField(
        verbose_name='CPF',
        max_length=11,
        blank=True,
        validators=[validate_cpf],
    )
    telefone = models.CharField(
        verbose_name='Telefone',
        max_length=11,
        blank=True,
        validators=[validate_telefone],
    )
    foto = models.ImageField(
        verbose_name='Foto',
        upload_to='professores/',
        null=True,
        blank=True,
    )
    ativo = models.BooleanField(verbose_name='Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'
        ordering = ['usuario__nome']

    def __str__(self):
        return self.usuario.nome

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = normalizar_cpf(self.cpf)
        if self.telefone:
            self.telefone = normalizar_telefone(self.telefone)
        super().save(*args, **kwargs)
