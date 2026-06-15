from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import RedirectView, TemplateView

from .models import UsuarioEscola


# ---------------------------------------------------------------------------
# Views públicas
# ---------------------------------------------------------------------------

class Index(RedirectView):
    pattern_name = 'blog:noticias'
    permanent = False


class Contato(TemplateView):
    template_name = 'core/contate_nos.html'


class Sobre(TemplateView):
    template_name = 'core/sobre.html'


# ---------------------------------------------------------------------------
# Base para dashboards autenticados
# ---------------------------------------------------------------------------

class BaseDashboardView(TemplateView):
    """
    Classe base para todas as views de dashboard do sistema.

    Garante, em toda requisição:
      1. Usuário autenticado
      2. Contexto de escola injetado pelo EscolaMiddleware (request.escola + request.vinculo)
      3. Tipo de usuário autorizado conforme tipo_permitido

    Injeta automaticamente no contexto do template:
      {{ escola }}   — UnidadeEscolar atual da sessão
      {{ vinculo }}  — UsuarioEscola com tipo e status do vínculo
      {{ usuario }}  — Usuário logado

    Uso:
        class ProfessorDashboard(BaseDashboardView):
            template_name = 'professor/dashboard.html'
            tipo_permitido = [UsuarioEscola.PROFESSOR]
    """

    template_name: str | None = None
    tipo_permitido: list = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        escola = getattr(request, 'escola', None)
        vinculo = getattr(request, 'vinculo', None)

        if escola is None or vinculo is None:
            return redirect('escola:selecionar')

        if self.tipo_permitido and vinculo.tipo_usuario not in self.tipo_permitido:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escola'] = self.request.escola
        context['vinculo'] = self.request.vinculo
        context['usuario'] = self.request.user
        context['tem_multiplas_escolas'] = getattr(
            self.request, 'tem_multiplas_escolas', False
        )
        return context
