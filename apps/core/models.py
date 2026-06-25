from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_platform_admin', True)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    nome              = models.CharField('Nome', max_length=150)
    email             = models.EmailField('E-mail', unique=True)
    foto              = models.ImageField('Foto', upload_to='usuarios/fotos/', null=True, blank=True)
    is_active         = models.BooleanField('Ativo', default=True)
    is_staff          = models.BooleanField('Staff', default=False)
    is_platform_admin = models.BooleanField('Admin da Plataforma', default=False)
    data_criacao      = models.DateTimeField('Criado em', auto_now_add=True)
    data_atualizacao  = models.DateTimeField('Atualizado em', auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        verbose_name        = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.nome} ({self.email})'

    @property
    def primeiro_nome(self):
        return self.nome.split()[0] if self.nome else ''


class TipoVinculo(models.TextChoices):
    DIRETOR     = 'DIRETOR',     'Diretor'
    FUNCIONARIO = 'FUNCIONARIO', 'Funcionário'
    PROFESSOR   = 'PROFESSOR',   'Professor'
    ALUNO       = 'ALUNO',       'Aluno'
    RESPONSAVEL = 'RESPONSAVEL', 'Responsável'


class VinculoEscola(models.Model):
    usuario      = models.ForeignKey(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='vinculos',
        verbose_name='Usuário',
    )
    escola       = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='vinculos',
        verbose_name='Escola',
    )
    ativo        = models.BooleanField('Ativo', default=True)
    data_entrada = models.DateTimeField('Data de entrada', auto_now_add=True)

    class Meta:
        verbose_name        = 'Vínculo Escola'
        verbose_name_plural = 'Vínculos Escola'
        unique_together     = ('usuario', 'escola')

    def __str__(self):
        return f'{self.usuario.nome} — {self.escola}'


class PapelVinculo(models.Model):
    vinculo = models.ForeignKey(
        VinculoEscola,
        on_delete=models.CASCADE,
        related_name='papeis',
        verbose_name='Vínculo',
    )
    tipo    = models.CharField('Tipo', max_length=20, choices=TipoVinculo.choices)
    ativo   = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Papel do Vínculo'
        verbose_name_plural = 'Papéis do Vínculo'
        unique_together     = ('vinculo', 'tipo')

    def __str__(self):
        return f'{self.vinculo.usuario.nome} — {self.get_tipo_display()} em {self.vinculo.escola}'

    @property
    def escola(self):
        return self.vinculo.escola

    @property
    def usuario(self):
        return self.vinculo.usuario


class Endereco(models.Model):
    cep         = models.CharField('CEP', max_length=9, blank=True)
    logradouro  = models.CharField('Logradouro', max_length=200)
    numero      = models.CharField('Número', max_length=20)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro      = models.CharField('Bairro', max_length=100)
    municipio   = models.CharField('Município', max_length=100)
    uf          = models.CharField('UF', max_length=2)

    class Meta:
        verbose_name        = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f'{self.logradouro}, {self.numero} — {self.municipio}/{self.uf}'
