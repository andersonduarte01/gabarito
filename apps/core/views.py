from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View

from .models import VinculoEscola, TipoVinculo


class ModuloRequiredMixin:
    """
    Verifica se um módulo está ativo para a escola do request.
    Define modulo_requerido = CodigoModulo.ALGUMA_COISA na subclasse.
    Só verifica se apps.planos estiver instalado.
    """

    modulo_requerido: str | None = None

    def dispatch(self, request, *args, **kwargs):
        if self.modulo_requerido:
            from django.apps import apps as django_apps
            if django_apps.is_installed('apps.planos'):
                from apps.planos.services import assinatura_service
                escola = getattr(request, 'escola', None)
                if escola and not assinatura_service.modulo_ativo(escola, self.modulo_requerido):
                    raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class Index(TemplateView):
    template_name = 'core/index.html'


class Contato(TemplateView):
    template_name = 'core/contate_nos.html'


class Sobre(TemplateView):
    template_name = 'core/sobre.html'


# ---------------------------------------------------------------------------
# Base para dashboards autenticados
# ---------------------------------------------------------------------------

class BaseDashboardView(TemplateView):
    """
    Classe base para todas as views de dashboard.

    Garante em toda requisição:
      1. Usuário autenticado
      2. request.papel injetado pelo TenantMiddleware
      3. Tipo de papel autorizado conforme tipos_permitidos

    Injeta no contexto:
      {{ papel }}   — PapelVinculo ativo
      {{ vinculo }} — VinculoEscola
      {{ escola }}  — UnidadeEscolar
      {{ usuario }} — Usuário logado

    Uso:
        class DiretorDashboard(BaseDashboardView):
            template_name  = 'diretor/dashboard.html'
            tipos_permitidos = [TipoVinculo.DIRETOR]
    """

    template_name:    str | None = None
    tipos_permitidos: list       = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        papel = getattr(request, 'papel', None)
        if papel is None:
            return redirect('core:selecionar_escola')

        if self.tipos_permitidos and papel.tipo not in self.tipos_permitidos:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['papel']   = self.request.papel
        context['vinculo'] = self.request.vinculo
        context['escola']  = self.request.escola
        context['usuario'] = self.request.user
        return context


# ---------------------------------------------------------------------------
# Roteamento pós-login
# ---------------------------------------------------------------------------

class DashboardRedirectView(View):
    """Redireciona para o dashboard do papel ativo após login."""

    # Atualizado à medida que os módulos são implementados
    DESTINOS = {
        TipoVinculo.DIRETOR:     'diretor:dashboard',  # módulo 07
        TipoVinculo.FUNCIONARIO: 'core:inicio',   # módulo 08
        TipoVinculo.PROFESSOR:   'core:inicio',   # módulo 09
        TipoVinculo.ALUNO:       'core:inicio',   # módulo 15
        TipoVinculo.RESPONSAVEL: 'core:inicio',   # módulo 10
    }

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.is_platform_admin:
            return redirect('core:inicio')  # módulo plataforma (futuro)

        papel = getattr(request, 'papel', None)
        if papel is None:
            return redirect('core:selecionar_escola')

        destino = self.DESTINOS.get(papel.tipo, 'core:inicio')
        return redirect(destino)


# ---------------------------------------------------------------------------
# Seleção de escola e papel
# ---------------------------------------------------------------------------

class SelecionarEscolaView(View):
    template_name = 'core/selecionar_escola.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        vinculos = (
            VinculoEscola.objects
            .filter(usuario=request.user, ativo=True)
            .select_related('escola')
            .prefetch_related('papeis')
        )
        return render(request, self.template_name, {'vinculos': vinculos})

    def post(self, request):
        vinculo_id = request.POST.get('vinculo_id')
        try:
            vinculo = VinculoEscola.objects.prefetch_related('papeis').get(
                pk=vinculo_id, usuario=request.user, ativo=True
            )
        except VinculoEscola.DoesNotExist:
            return redirect('core:selecionar_escola')

        papeis_ativos = list(vinculo.papeis.filter(ativo=True))
        if not papeis_ativos:
            return redirect('core:selecionar_escola')

        if len(papeis_ativos) == 1:
            request.session['papel_id'] = papeis_ativos[0].pk
            return redirect('core:dashboard')

        request.session['vinculo_selecionado'] = vinculo.pk
        return redirect('core:selecionar_papel')


class SelecionarPapelView(View):
    template_name = 'core/selecionar_papel.html'

    def _get_vinculo_e_papeis(self, request):
        vinculo_id = request.session.get('vinculo_selecionado')
        if not vinculo_id:
            qs = VinculoEscola.objects.filter(usuario=request.user, ativo=True)
            if qs.count() == 1:
                vinculo_id = qs.values_list('pk', flat=True).first()
        if not vinculo_id:
            return None, []
        try:
            vinculo = (
                VinculoEscola.objects
                .select_related('escola')
                .get(pk=vinculo_id, usuario=request.user, ativo=True)
            )
        except VinculoEscola.DoesNotExist:
            return None, []
        return vinculo, list(vinculo.papeis.filter(ativo=True))

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        vinculo, papeis = self._get_vinculo_e_papeis(request)
        if not papeis:
            return redirect('core:selecionar_escola')
        return render(request, self.template_name, {'vinculo': vinculo, 'papeis': papeis})

    def post(self, request):
        papel_id = request.POST.get('papel_id')
        vinculo, papeis = self._get_vinculo_e_papeis(request)
        ids_validos = {str(p.pk) for p in papeis}
        if papel_id not in ids_validos:
            return redirect('core:selecionar_papel')
        request.session['papel_id'] = int(papel_id)
        request.session.pop('vinculo_selecionado', None)
        return redirect('core:dashboard')
