from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None):
        if not email:
            raise ValueError('Digite um email válido.')
        user = self.model(
            email=self.normalize_email(email),
            nome=nome,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None):
        user = self.create_user(email, password=password, nome=nome)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser):
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    # ── Propriedades de papel — delegam ao through model UsuarioEscola ─────
    # Mantidas por compatibilidade com código legado; preferir request.vinculo.tipo

    @property
    def is_administrator(self):
        from apps.escola.models import UsuarioEscola
        return self.vinculos.filter(tipo=UsuarioEscola.ADMINISTRADOR, ativo=True).exists()

    @property
    def is_professor(self):
        from apps.escola.models import UsuarioEscola
        return self.vinculos.filter(tipo=UsuarioEscola.PROFESSOR, ativo=True).exists()

    @property
    def is_funcionario(self):
        from apps.escola.models import UsuarioEscola
        return self.vinculos.filter(tipo=UsuarioEscola.FUNCIONARIO, ativo=True).exists()

    @property
    def is_aluno(self):
        from apps.escola.models import UsuarioEscola
        return self.vinculos.filter(tipo=UsuarioEscola.ALUNO, ativo=True).exists()

    # ── Roteamento de dashboard ────────────────────────────────────────────

    def get_dashboard_url(self, escola=None):
        """Retorna URL de dashboard baseado no tipo do vínculo na escola."""
        from django.urls import reverse
        from apps.escola.models import UsuarioEscola

        qs = self.vinculos.filter(ativo=True).select_related('escola')
        vinculo = qs.filter(escola=escola).first() if escola else qs.first()

        if not vinculo:
            return reverse('login')

        mapa = {
            UsuarioEscola.ADMINISTRADOR: 'escola:painel_adm',
            UsuarioEscola.PROFESSOR:     'funcionario:dash_professor',
            UsuarioEscola.FUNCIONARIO:   'funcionario:dash_funcionario',
            UsuarioEscola.ALUNO:         'alunos:dash_aluno',
        }
        return reverse(mapa.get(vinculo.tipo, 'escola:painel_escola'))
