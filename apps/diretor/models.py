from django.db import models


class CargoDiretor(models.TextChoices):
    TITULAR    = 'TITULAR',    'Titular'
    SUBSTITUTO = 'SUBSTITUTO', 'Substituto'
    ADJUNTO    = 'ADJUNTO',    'Adjunto'


class PerfilDiretor(models.Model):
    papel           = models.OneToOneField(
        'core.PapelVinculo',
        on_delete=models.CASCADE,
        related_name='perfil_diretor',
        verbose_name='Papel',
    )
    endereco        = models.OneToOneField(
        'core.Endereco',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_diretor',
        verbose_name='Endereço',
    )
    cpf             = models.CharField('CPF', max_length=14, blank=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    telefone        = models.CharField('Telefone', max_length=20, blank=True)
    foto            = models.ImageField('Foto', upload_to='diretores/fotos/', null=True, blank=True)
    cargo           = models.CharField(
        'Cargo',
        max_length=15,
        choices=CargoDiretor.choices,
        default=CargoDiretor.TITULAR,
    )
    numero_ato      = models.CharField('Nº do Ato', max_length=50, blank=True)
    data_ato        = models.DateField('Data do Ato', null=True, blank=True)
    data_inicio     = models.DateField('Data de Início', null=True, blank=True)
    criado_em       = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em   = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Perfil do Diretor'
        verbose_name_plural = 'Perfis de Diretores'

    def __str__(self):
        return f'{self.papel.usuario.nome} ({self.get_cargo_display()}) — {self.papel.escola}'

    @property
    def escola(self):
        return self.papel.escola

    @property
    def usuario(self):
        return self.papel.usuario
