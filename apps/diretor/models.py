from django.db import models

from apps.core.validators import validate_cpf, validate_telefone, normalizar_cpf, normalizar_telefone


class Diretor(models.Model):
    """
    Perfil de diretor vinculado a uma escola específica.

    - `usuario` é ForeignKey: a mesma pessoa pode ser diretora em escolas
      diferentes (ou ter outro papel em outra escola via UsuarioEscola).
    - `escola` é OneToOneField: cada escola tem exatamente um diretor ativo,
      garantido em nível de banco de dados.
    """

    usuario = models.ForeignKey(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='cargos_diretor',
        verbose_name='Usuário',
    )
    escola = models.OneToOneField(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='diretor',
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
        upload_to='diretores/',
        null=True,
        blank=True,
    )
    ativo = models.BooleanField(verbose_name='Ativo', default=True)
    criado_em = models.DateTimeField(verbose_name='Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Diretor'
        verbose_name_plural = 'Diretores'
        ordering = ['usuario__nome']

    def __str__(self):
        return f'{self.usuario.nome} — {self.escola.nome_escola}'

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = normalizar_cpf(self.cpf)
        if self.telefone:
            self.telefone = normalizar_telefone(self.telefone)
        super().save(*args, **kwargs)
