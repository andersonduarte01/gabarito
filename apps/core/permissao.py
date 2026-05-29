from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import UsuarioEscola


class PermissaoRequiredMixin(LoginRequiredMixin):
    """
    Mixin de controle de acesso por tipo de usuário na escola.

    Uso:
        class MinhaView(PermissaoRequiredMixin, TemplateView):
            permissao_tipos = [UsuarioEscola.PROFESSOR, UsuarioEscola.DIRETOR]

    Atributos:
        permissao_tipos  — lista/tupla/set de tipos permitidos (prioridade)
        permissao_tipo   — tipo único (compatibilidade, use permissao_tipos de preferência)

    Quando permissao_tipos é None/vazio, apenas autenticação é exigida
    (qualquer tipo de vínculo ativo tem acesso).

    Depende do EscolaMiddleware para injetar request.escola e request.vinculo.
    Se o middleware não injetou o vínculo, tenta recuperar via fallback seguro.
    """

    permissao_tipo: str | None = None
    permissao_tipos: list | tuple | set | None = None
    login_url = 'accounts:login'
    redirect_field_name = 'next'

    def _get_tipos_permitidos(self) -> set | None:
        if self.permissao_tipos:
            if isinstance(self.permissao_tipos, str):
                return {self.permissao_tipos}
            return set(self.permissao_tipos)
        if self.permissao_tipo:
            return {self.permissao_tipo}
        return None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        vinculo = getattr(request, 'vinculo', None)

        # Fallback: middleware pode não ter rodado (ex.: admin, testes)
        if vinculo is None:
            escola = getattr(request, 'escola', None)
            if escola is None:
                raise PermissionDenied

            try:
                vinculo = UsuarioEscola.objects.get(
                    usuario=request.user,
                    escola=escola,
                    ativo=True,
                )
                request.vinculo = vinculo
            except UsuarioEscola.DoesNotExist:
                raise PermissionDenied

        tipos_permitidos = self._get_tipos_permitidos()

        if tipos_permitidos and vinculo.tipo_usuario not in tipos_permitidos:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
