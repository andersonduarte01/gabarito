from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from django.urls import reverse


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
        if not extra_fields.get('is_staff'):
            raise ValueError('Superusuário deve ter is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superusuário deve ter is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(verbose_name='Nome', max_length=150)
    email = models.EmailField(verbose_name='Email', unique=True)
    is_active = models.BooleanField(verbose_name='Ativo', default=True)
    is_staff = models.BooleanField(verbose_name='Equipe', default=False)
    data_criacao = models.DateTimeField(verbose_name='Criado em', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Atualizado em', auto_now=True)

    escolas = models.ManyToManyField(
        'escola.UnidadeEscolar',
        through='UsuarioEscola',
        related_name='usuarios',
        blank=True,
        verbose_name='Escolas',
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.nome} ({self.email})'

    def get_dashboard_url(self, escola):
        try:
            self.usuarioescola_set.get(escola=escola, ativo=True)
            return reverse('escola:dash_escola')
        except UsuarioEscola.DoesNotExist:
            return reverse('accounts:login')

    def remover_escola(self, escola):
        self.usuarioescola_set.filter(escola=escola).update(ativo=False)
        if not self.usuarioescola_set.filter(ativo=True).exists():
            self.is_active = False
            self.save(update_fields=['is_active'])


class UsuarioEscola(models.Model):
    DIRETOR     = 'DIR'
    COLABORADOR = 'COLAB'
    PROFESSOR   = 'PROF'
    ALUNO       = 'ALUNO'

    TIPOS = [
        (DIRETOR,     'Diretor'),
        (COLABORADOR, 'Colaborador'),
        (PROFESSOR,   'Professor'),
        (ALUNO,       'Aluno'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usuarioescola_set',
        verbose_name='Usuário',
    )
    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='vinculos',
        verbose_name='Escola',
    )
    tipo_usuario = models.CharField(
        verbose_name='Tipo de Usuário',
        max_length=10,
        choices=TIPOS,
    )
    ativo = models.BooleanField(verbose_name='Ativo', default=True)
    data_vinculo = models.DateTimeField(verbose_name='Data do Vínculo', auto_now_add=True)

    class Meta:
        verbose_name = 'Vínculo Escola'
        verbose_name_plural = 'Vínculos Escola'
        unique_together = ('usuario', 'escola')

    def __str__(self):
        return f'{self.usuario.nome} — {self.escola} ({self.get_tipo_usuario_display()})'
