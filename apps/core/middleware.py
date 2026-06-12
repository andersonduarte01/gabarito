from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import resolve, Resolver404
from django.utils.deprecation import MiddlewareMixin


# Rotas acessíveis sem escola na sessão (públicas ou de auth)
_ROTAS_LIVRES = frozenset([
    # Páginas públicas
    'core:inicio', 'core:sobre', 'core:contato',
    'core:arquivos', 'core:arquivos_pesquisados',
    'core:biblioteca', 'core:livros_pesquisados',
    'core:videos', 'core:videos_pesquisados', 'core:ano_materia',
    # Blog
    'blog:noticias', 'blog:noticia', 'blog:noticias_pesquisadas',
    # Auth Django
    'login', 'logout',
    'password_reset', 'password_reset_done',
    'password_reset_confirm', 'password_reset_complete',
    'password_change', 'password_change_done',
    # Seleção de escola (seria loop infinito se bloqueasse)
    'escola:selecionar_escola',
])


class EscolaMiddleware(MiddlewareMixin):
    """
    Injeta `request.escola` (UnidadeEscolar) e `request.vinculo` (UsuarioEscola)
    em cada request autenticado. Garante o isolamento de dados por tenant.

    Fluxo:
        1. Rotas livres → passa direto
        2. Usuário não autenticado → passa (Django auth cuida do redirect)
        3. Sem escola na sessão → auto-seleciona se apenas 1; senão redireciona
        4. Escola/vínculo inválido → limpa sessão e redireciona
        5. Tudo OK → injeta request.escola, request.vinculo, request.tem_multiplas_escolas
    """

    def process_request(self, request):
        # Inicializa atributos — sempre disponíveis nos templates/views
        request.escola = None
        request.vinculo = None
        request.tem_multiplas_escolas = False

        # Admin Django e API têm suas próprias proteções
        if request.path.startswith('/admin/') or request.path.startswith('/api/'):
            return

        # Resolve nome da rota para comparar com rotas livres
        try:
            match = resolve(request.path_info)
            ns = match.namespace or ''
            nome_completo = f"{ns}:{match.url_name}" if ns else match.url_name
            if nome_completo in _ROTAS_LIVRES or match.url_name in _ROTAS_LIVRES:
                return
        except Resolver404:
            return

        # Sem autenticação → Django redireciona para login por conta própria
        if not request.user.is_authenticated:
            return

        escola_id = request.session.get('escola_id')

        if not escola_id:
            return self._handle_sem_escola(request)

        # Importação lazy para evitar circular import no carregamento do módulo
        from apps.escola.models import UnidadeEscolar, UsuarioEscola

        try:
            escola = UnidadeEscolar.objects.get(id=escola_id, ativa=True)
        except UnidadeEscolar.DoesNotExist:
            return self._limpar_e_redirecionar(request)

        try:
            vinculo = UsuarioEscola.objects.select_related('escola', 'usuario').get(
                usuario=request.user,
                escola=escola,
                ativo=True,
            )
        except UsuarioEscola.DoesNotExist:
            return self._limpar_e_redirecionar(request)

        # ✅ Contexto de tenant injetado com sucesso
        request.escola = escola
        request.vinculo = vinculo
        request.tem_multiplas_escolas = (
            UsuarioEscola.objects
            .filter(usuario=request.user, ativo=True)
            .count() > 1
        )

    # ── Helpers ────────────────────────────────────────────────────────────

    def _handle_sem_escola(self, request):
        """Usuário logado mas sem escola na sessão."""
        from apps.escola.models import UsuarioEscola

        vinculos = (
            UsuarioEscola.objects
            .filter(usuario=request.user, ativo=True)
            .select_related('escola')
        )

        if not vinculos.exists():
            logout(request)
            return redirect('login')

        # Auto-seleção quando há apenas uma escola
        if vinculos.count() == 1:
            request.session['escola_id'] = vinculos.first().escola_id
            return  # Deixa a request continuar normalmente

        return redirect('escola:selecionar_escola')

    def _limpar_e_redirecionar(self, request):
        """Remove escola inválida da sessão e decide para onde ir."""
        request.session.pop('escola_id', None)
        from apps.escola.models import UsuarioEscola

        vinculos = UsuarioEscola.objects.filter(usuario=request.user, ativo=True)

        if not vinculos.exists():
            logout(request)
            return redirect('login')

        return redirect('escola:selecionar_escola')
