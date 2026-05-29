from django.contrib.auth import get_user_model
from django.db import transaction

from .models import UsuarioEscola
from .validators import normalizar_cpf

Usuario = get_user_model()


# ---------------------------------------------------------------------------
# UsuarioService
# ---------------------------------------------------------------------------

class UsuarioService:
    """
    Serviço central para criação e gestão de usuários vinculados a uma escola.

    Garante atomicidade, unicidade por email/CPF e reativação de vínculos inativos.

    Uso:
        service = UsuarioService(escola=minha_escola)
        result = service.processar_usuario(
            email='prof@escola.com',
            nome='Maria Silva',
            tipo_usuario=UsuarioEscola.PROFESSOR,
            password='senha123',
        )
        if result['status'] == 'ok':
            usuario = result['usuario']
    """

    def __init__(self, escola):
        self.escola = escola

    @transaction.atomic
    def processar_usuario(
        self,
        *,
        email: str,
        nome: str,
        tipo_usuario: str,
        password: str,
        cpf: str | None = None,
        perfil_model=None,
        perfil_data: dict | None = None,
    ) -> dict:
        """
        Cria ou reutiliza um usuário e garante o vínculo com a escola.

        Retorna dict com:
            status  — 'ok' (criado), 'exists' (reaproveitado), 'error'
            message — descrição legível
            usuario — instância de Usuario ou None em caso de erro
            perfil  — instância do perfil complementar ou None
        """
        try:
            if cpf:
                cpf = normalizar_cpf(cpf)
                conflito = self._buscar_por_cpf(cpf)
                if conflito and conflito.email != email:
                    return self._erro(
                        f'CPF já cadastrado para outro usuário ({conflito.email}).'
                    )

            usuario, criado = self._obter_ou_criar_usuario(email, nome, password)

            perfil = None
            if perfil_model and perfil_data:
                perfil = self._processar_perfil(usuario, perfil_model, perfil_data)

            resultado_vinculo = self._vincular_escola(usuario, tipo_usuario)
            if resultado_vinculo:
                return {**resultado_vinculo, 'usuario': usuario, 'perfil': perfil}

            return {
                'status': 'ok' if criado else 'exists',
                'message': (
                    'Usuário criado com sucesso.'
                    if criado
                    else 'Usuário já existia e foi vinculado à escola.'
                ),
                'usuario': usuario,
                'perfil': perfil,
            }

        except Exception as exc:
            return self._erro(f'Erro inesperado: {exc}')

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _obter_ou_criar_usuario(self, email: str, nome: str, password: str):
        try:
            return Usuario.objects.get(email=email), False
        except Usuario.DoesNotExist:
            return Usuario.objects.create_user(email=email, nome=nome, password=password), True

    def _vincular_escola(self, usuario, tipo_usuario: str) -> dict | None:
        """
        Cria ou valida o vínculo do usuário com a escola.
        Retorna None se tudo OK, ou dict de erro/exists se houver conflito.
        """
        vinculo, criado = UsuarioEscola.objects.get_or_create(
            usuario=usuario,
            escola=self.escola,
            defaults={'tipo_usuario': tipo_usuario, 'ativo': True},
        )

        if not criado:
            if vinculo.tipo_usuario != tipo_usuario:
                return {
                    'status': 'exists',
                    'message': (
                        f'Usuário já vinculado a esta escola como '
                        f'"{vinculo.get_tipo_usuario_display()}".'
                    ),
                    'perfil': None,
                }
            if not vinculo.ativo:
                vinculo.ativo = True
                vinculo.save(update_fields=['ativo'])

        if not usuario.is_active:
            usuario.is_active = True
            usuario.save(update_fields=['is_active'])

        return None

    def _processar_perfil(self, usuario, perfil_model, perfil_data: dict):
        """Cria ou recupera o perfil complementar vinculado ao usuário."""
        perfil, _ = perfil_model.objects.get_or_create(
            usuario=usuario,
            defaults=perfil_data,
        )
        return perfil

    def _buscar_por_cpf(self, cpf: str):
        """
        Busca um usuário pelo CPF em todos os modelos de perfil ativos.
        Usa imports tardios para suportar apps parcialmente habilitados.
        """
        for buscar in (
            self._cpf_via_aluno,
            self._cpf_via_professor,
            self._cpf_via_colaborador,
        ):
            try:
                usuario = buscar(cpf)
                if usuario:
                    return usuario
            except Exception:
                continue
        return None

    def _cpf_via_aluno(self, cpf: str):
        from apps.aluno.models import Aluno
        aluno = Aluno.objects.select_related('usuario').filter(cpf=cpf).first()
        return getattr(aluno, 'usuario', None)

    def _cpf_via_professor(self, cpf: str):
        from apps.colaborador.models import Professor
        professor = Professor.objects.select_related('usuario').filter(cpf=cpf).first()
        return getattr(professor, 'usuario', None)

    def _cpf_via_colaborador(self, cpf: str):
        from apps.colaborador.models import Colaborador
        colaborador = Colaborador.objects.select_related('usuario').filter(cpf=cpf).first()
        return getattr(colaborador, 'usuario', None)

    @staticmethod
    def _erro(message: str) -> dict:
        return {'status': 'error', 'message': message, 'usuario': None, 'perfil': None}


# ---------------------------------------------------------------------------
# AlunoService
# ---------------------------------------------------------------------------

class AlunoService:
    """
    Serviço específico para criação de alunos com vínculo escolar.

    Regra de negócio:
        - Com responsável  → aluno não faz login; email é institucional
                             gerado automaticamente; is_active=False
        - Sem responsável  → aluno tem login próprio; email real obrigatório;
                             is_active=True

    Uso:
        service = AlunoService(escola=minha_escola)
        result = service.criar_aluno(
            nome='João Souza',
            cpf='12345678909',
            data_nascimento='2010-05-20',
            sala=sala_obj,
            tem_responsavel=True,
        )
    """

    EMAIL_INSTITUCIONAL_DOMINIO = 'aluno.interno'

    def __init__(self, escola):
        self.escola = escola

    @transaction.atomic
    def criar_aluno(
        self,
        *,
        nome: str,
        cpf: str,
        data_nascimento: str,
        sala,
        tem_responsavel: bool,
        email: str | None = None,
        password: str | None = None,
        sexo: str = 'M',
    ) -> dict:
        """
        Cria um aluno com perfil de usuário e vínculo escolar.

        Retorna dict com:
            status  — 'created', 'exists', 'error'
            message — descrição legível
            aluno   — instância de Aluno ou None
            usuario — instância de Usuario ou None
        """
        try:
            from apps.aluno.models import Aluno

            cpf = normalizar_cpf(cpf)
            if not cpf:
                return self._erro('CPF é obrigatório.')

            # Aluno já cadastrado nesta escola?
            aluno_existente = Aluno.objects.filter(
                cpf=cpf,
                sala__escola=self.escola,
            ).first()
            if aluno_existente:
                self._garantir_vinculo(aluno_existente.usuario)
                return {
                    'status': 'exists',
                    'message': 'Aluno já cadastrado nesta escola.',
                    'aluno': aluno_existente,
                    'usuario': aluno_existente.usuario,
                }

            email_login, ativo, senha = self._resolver_credenciais(
                nome=nome,
                cpf=cpf,
                email=email,
                password=password,
                tem_responsavel=tem_responsavel,
            )

            usuario = Usuario.objects.create_user(
                email=email_login,
                nome=nome,
                password=senha,
                is_active=ativo,
            )

            UsuarioEscola.objects.create(
                usuario=usuario,
                escola=self.escola,
                tipo_usuario=UsuarioEscola.ALUNO,
                ativo=True,
            )

            aluno = Aluno.objects.create(
                cpf=cpf,
                data_nascimento=data_nascimento,
                sexo=sexo,
                sala=sala,
                escola=self.escola,
                usuario=usuario,
            )

            return {
                'status': 'created',
                'message': 'Aluno cadastrado com sucesso.',
                'aluno': aluno,
                'usuario': usuario,
            }

        except Exception as exc:
            return self._erro(f'Erro ao cadastrar aluno: {exc}')

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _resolver_credenciais(
        self, *, nome: str, cpf: str, email, password, tem_responsavel: bool
    ) -> tuple[str, bool, str | None]:
        """
        Retorna (email_login, is_active, password) conforme regra de responsável.
        """
        if tem_responsavel:
            slug = cpf[-6:]
            email_login = f'aluno.{slug}@{self.EMAIL_INSTITUCIONAL_DOMINIO}'
            return email_login, False, None

        if not email:
            raise ValueError('Email é obrigatório para aluno sem responsável.')
        if not password:
            raise ValueError('Senha é obrigatória para aluno sem responsável.')

        return email, True, password

    def _garantir_vinculo(self, usuario) -> None:
        """Reativa ou cria o vínculo do aluno com a escola atual."""
        vinculo, criado = UsuarioEscola.objects.get_or_create(
            usuario=usuario,
            escola=self.escola,
            defaults={'tipo_usuario': UsuarioEscola.ALUNO, 'ativo': True},
        )
        if not criado and not vinculo.ativo:
            vinculo.ativo = True
            vinculo.save(update_fields=['ativo'])

    @staticmethod
    def _erro(message: str) -> dict:
        return {'status': 'error', 'message': message, 'aluno': None, 'usuario': None}
