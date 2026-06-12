from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy


class EscolaContextMixin(LoginRequiredMixin):
    """
    Garante autenticação + escola ativa na sessão.
    Qualquer view do sistema interno deve herdar deste mixin.
    """
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Middleware já tentou injetar request.escola.
        # Se ainda for None, redireciona para seleção.
        if getattr(request, 'escola', None) is None:
            return redirect('escola:selecionar_escola')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escola_atual'] = self.request.escola
        context['vinculo_atual'] = self.request.vinculo
        return context


class PermissaoEscolaMixin(EscolaContextMixin):
    """
    RBAC por tenant: restringe acesso a tipos de usuário específicos.

    Uso:
        class MinhaDashView(PermissaoEscolaMixin, TemplateView):
            tipos_permitidos = [UsuarioEscola.ADMINISTRADOR]
    """
    tipos_permitidos: list = []  # ex: ['ADM'], ['PROF', 'ADM']

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        # super() pode ter devolvido um redirect (não autenticado / sem escola)
        if hasattr(response, 'status_code') and response.status_code in (301, 302):
            return response

        vinculo = getattr(request, 'vinculo', None)
        if vinculo is None:
            raise PermissionDenied('Sem vínculo com a escola atual.')

        if self.tipos_permitidos and vinculo.tipo not in self.tipos_permitidos:
            raise PermissionDenied(
                f'Acesso restrito a: '
                f'{", ".join(t for t in self.tipos_permitidos)}.'
            )

        return response


# ── Superadmin (sem contexto de escola) ───────────────────────────────────

class SuperAdminMixin(LoginRequiredMixin):
    """
    Acesso exclusivo para superadministradores (Usuario.is_admin = True).
    Não exige escola na sessão — opera acima do contexto de tenant.
    """
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not getattr(request.user, 'is_admin', False):
            raise PermissionDenied('Área restrita ao superadministrador.')
        return super().dispatch(request, *args, **kwargs)


# ── Atalhos semânticos ─────────────────────────────────────────────────────

class ApenasAdminMixin(PermissaoEscolaMixin):
    """Somente Administradores."""
    from apps.escola.models import UsuarioEscola as _UE
    tipos_permitidos = [_UE.ADMINISTRADOR]


class ApenasProfessorMixin(PermissaoEscolaMixin):
    """Somente Professores."""
    from apps.escola.models import UsuarioEscola as _UE
    tipos_permitidos = [_UE.PROFESSOR]


class AdminOuProfessorMixin(PermissaoEscolaMixin):
    """Administradores e Professores."""
    from apps.escola.models import UsuarioEscola as _UE
    tipos_permitidos = [_UE.ADMINISTRADOR, _UE.PROFESSOR]


class StaffMixin(PermissaoEscolaMixin):
    """Administradores, Professores e Funcionários (exceto Alunos)."""
    from apps.escola.models import UsuarioEscola as _UE
    tipos_permitidos = [_UE.ADMINISTRADOR, _UE.PROFESSOR, _UE.FUNCIONARIO]
