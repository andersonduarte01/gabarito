from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse, NoReverseMatch

from .models import UsuarioEscola
from apps.escola.models import UnidadeEscolar


class EscolaMiddleware:
    """
    Injeta request.escola e request.vinculo em cada requisição autenticada.

    Fluxo:
      - Admin e API passam direto (autenticação própria)
      - Rotas públicas passam direto
      - Usuário sem autenticação passa direto (LoginRequired da view cuida disso)
      - 0 vínculos ativos  → logout + redirect login
      - 1 vínculo ativo    → seleciona automaticamente
      - N vínculos ativos  → redirect para tela de seleção de escola
    """

    # /accounts/ cobre login, logout e todo o fluxo de senha — todos são públicos
    PREFIXOS_IGNORADOS = ('/admin/', '/api/', '/static/', '/media/', '/accounts/')

    ROTAS_PUBLICAS = (
        'escola:selecionar',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resposta = self._processar(request)
        if resposta:
            return resposta
        return self.get_response(request)

    # ------------------------------------------------------------------
    # Processamento principal
    # ------------------------------------------------------------------

    def _processar(self, request):
        if self._deve_ignorar(request):
            return None

        if not request.user.is_authenticated:
            return None

        escola_id = request.session.get('escola_id')

        if not escola_id:
            return self._handle_sem_escola(request)

        # Valida escola ativa
        try:
            escola = UnidadeEscolar.objects.get(pk=escola_id, ativo=True)
        except UnidadeEscolar.DoesNotExist:
            return self._limpar_sessao(request)

        # Valida vínculo ativo do usuário com a escola
        try:
            vinculo = (
                UsuarioEscola.objects
                .select_related('escola')
                .get(usuario=request.user, escola=escola, ativo=True)
            )
        except UsuarioEscola.DoesNotExist:
            return self._limpar_sessao(request)

        request.escola = escola
        request.vinculo = vinculo
        request.tem_multiplas_escolas = (
            UsuarioEscola.objects
            .filter(usuario=request.user, ativo=True)
            .count() > 1
        )

        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _deve_ignorar(self, request):
        path = request.path_info

        for prefixo in self.PREFIXOS_IGNORADOS:
            if path.startswith(prefixo):
                return True

        for nome in self.ROTAS_PUBLICAS:
            try:
                if path == reverse(nome):
                    return True
            except NoReverseMatch:
                continue

        return False

    def _handle_sem_escola(self, request):
        vinculos = (
            UsuarioEscola.objects
            .filter(usuario=request.user, ativo=True)
            .select_related('escola')
        )

        if not vinculos.exists():
            logout(request)
            return HttpResponseRedirect(reverse('accounts:login'))

        if vinculos.count() == 1:
            vinculo = vinculos.first()
            escola = vinculo.escola
            request.session['escola_id'] = escola.pk
            request.escola = escola
            request.vinculo = vinculo
            request.tem_multiplas_escolas = False
            return None

        return self._redirecionar_selecao()

    def _limpar_sessao(self, request):
        request.session.pop('escola_id', None)

        if not UsuarioEscola.objects.filter(usuario=request.user, ativo=True).exists():
            logout(request)
            return HttpResponseRedirect(reverse('accounts:login'))

        return self._redirecionar_selecao()

    def _redirecionar_selecao(self):
        try:
            return HttpResponseRedirect(reverse('escola:selecionar'))
        except NoReverseMatch:
            return None
