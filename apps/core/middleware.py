from django.apps import apps as django_apps
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse, NoReverseMatch

from .models import PapelVinculo, VinculoEscola


class TenantMiddleware:
    """
    Injeta request.papel, request.vinculo e request.escola em cada requisição
    autenticada de usuários não-plataforma.

    Sessão armazena papel_id (PapelVinculo.id).

    Fluxo pós-login:
      0 vínculos ativos             → logout
      1 escola · 1 papel            → injeta direto
      1 escola · N papéis           → tela seleção de papel
      N escolas                     → tela seleção de escola
        └─ escola com 1 papel       → injeta direto
        └─ escola com N papéis      → tela seleção de papel

    Após injetar escola, verifica assinatura:
      TRIAL válido                  → passa (todos os módulos ativos)
      TRIAL expirado no dia         → expirar_trial() + redireciona acesso_bloqueado
      ATIVA                         → passa
      GRACE                         → passa + seta request.grace_dias_restantes
      TRIAL_EXPIRADO / SUSPENSA
        / CANCELADA                 → redireciona acesso_bloqueado
    """

    PREFIXOS_IGNORADOS = (
        '/admin/', '/api/', '/static/', '/media/', '/accounts/',
    )

    NOMES_IGNORADOS = (
        'core:inicio',
        'core:contato',
        'core:sobre',
        'core:selecionar_escola',
        'core:selecionar_papel',
        'planos:acesso_bloqueado',
    )

    def __init__(self, get_response):
        self.get_response     = get_response
        self._rotas_ignoradas = None  # resolvidas lazy para evitar AppRegistryNotReady

    def __call__(self, request):
        resposta = self._processar(request)
        if resposta:
            return resposta
        return self.get_response(request)

    # ------------------------------------------------------------------

    def _processar(self, request):
        if self._deve_ignorar(request):
            return None

        if not request.user.is_authenticated:
            return None

        if request.user.is_platform_admin:
            return None

        papel_id = request.session.get('papel_id')

        if not papel_id:
            return self._handle_sem_papel(request)

        try:
            papel = (
                PapelVinculo.objects
                .select_related('vinculo__escola', 'vinculo__usuario')
                .get(pk=papel_id, ativo=True, vinculo__ativo=True)
            )
        except PapelVinculo.DoesNotExist:
            return self._limpar_sessao(request)

        if papel.vinculo.usuario_id != request.user.pk:
            return self._limpar_sessao(request)

        request.papel   = papel
        request.vinculo = papel.vinculo
        request.escola  = papel.vinculo.escola

        return self._verificar_assinatura(request)

    # ------------------------------------------------------------------

    def _verificar_assinatura(self, request):
        if not django_apps.is_installed('apps.planos'):
            return None

        from apps.planos.models import AssinaturaEscola, StatusAssinatura
        from apps.planos.services import assinatura_service

        try:
            assinatura = request.escola.assinatura
        except AssinaturaEscola.DoesNotExist:
            return None  # escola sem assinatura criada ainda (não bloqueia)

        status = assinatura.status

        if status == StatusAssinatura.TRIAL:
            if not assinatura.trial_valido():
                assinatura_service.expirar_trial(assinatura)
                return HttpResponseRedirect(reverse('planos:acesso_bloqueado'))
            return None

        if status == StatusAssinatura.ATIVA:
            return None

        if status == StatusAssinatura.GRACE:
            request.grace_dias_restantes = assinatura.dias_restantes_grace()
            return None

        # TRIAL_EXPIRADO, SUSPENSA, CANCELADA
        return HttpResponseRedirect(reverse('planos:acesso_bloqueado'))

    # ------------------------------------------------------------------

    def _deve_ignorar(self, request):
        path = request.path_info
        for prefixo in self.PREFIXOS_IGNORADOS:
            if path.startswith(prefixo):
                return True
        if self._rotas_ignoradas is None:
            self._rotas_ignoradas = self._resolver_rotas()
        return path in self._rotas_ignoradas

    def _resolver_rotas(self):
        rotas = set()
        for nome in self.NOMES_IGNORADOS:
            try:
                rotas.add(reverse(nome))
            except NoReverseMatch:
                pass
        return rotas

    def _handle_sem_papel(self, request):
        vinculos = list(
            VinculoEscola.objects
            .filter(usuario=request.user, ativo=True)
            .select_related('escola')
            .prefetch_related('papeis')
        )

        if not vinculos:
            logout(request)
            return HttpResponseRedirect(reverse('accounts:login'))

        if len(vinculos) > 1:
            return HttpResponseRedirect(reverse('core:selecionar_escola'))

        vinculo       = vinculos[0]
        papeis_ativos = [p for p in vinculo.papeis.all() if p.ativo]

        if not papeis_ativos:
            logout(request)
            return HttpResponseRedirect(reverse('accounts:login'))

        if len(papeis_ativos) == 1:
            papel = papeis_ativos[0]
            request.session['papel_id'] = papel.pk
            request.papel   = papel
            request.vinculo = vinculo
            request.escola  = vinculo.escola
            return self._verificar_assinatura(request)

        return HttpResponseRedirect(reverse('core:selecionar_papel'))

    def _limpar_sessao(self, request):
        request.session.pop('papel_id', None)
        request.session.pop('vinculo_selecionado', None)
        return self._handle_sem_papel(request)
