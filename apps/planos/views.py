from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, View

from .forms import (
    AssinaturaAtivarForm,
    AssinaturaCancelarForm,
    AssinaturaGraceForm,
    AssinaturaSuspenderForm,
    PlanoForm,
)
from .models import AssinaturaEscola, Plano
from .services import assinatura_service


# ---------------------------------------------------------------------------
# Mixin de segurança — apenas Super Admin da plataforma
# ---------------------------------------------------------------------------

class PlatformAdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_platform_admin:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Tela de acesso bloqueado (trial expirado / suspensa / cancelada)
# ---------------------------------------------------------------------------

class AcessoBloqueadoView(TemplateView):
    template_name = 'planos/acesso_bloqueado.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola  = getattr(self.request, 'escola', None)
        if escola:
            try:
                context['assinatura'] = escola.assinatura
            except AssinaturaEscola.DoesNotExist:
                pass
        return context


# ---------------------------------------------------------------------------
# Planos
# ---------------------------------------------------------------------------

class ListarPlanosView(PlatformAdminRequiredMixin, View):
    template_name = 'planos/listar_planos.html'

    def get(self, request):
        planos = Plano.objects.prefetch_related('modulos').order_by('preco_mensal')
        return render(request, self.template_name, {
            'planos':  planos,
            'usuario': request.user,
        })


class CriarPlanoView(PlatformAdminRequiredMixin, View):
    template_name = 'planos/form_plano.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form':    PlanoForm(),
            'usuario': request.user,
            'titulo':  'Novo Plano',
        })

    def post(self, request):
        form = PlanoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plano criado com sucesso.')
            return redirect('planos:listar_planos')
        return render(request, self.template_name, {
            'form':    form,
            'usuario': request.user,
            'titulo':  'Novo Plano',
        })


class EditarPlanoView(PlatformAdminRequiredMixin, View):
    template_name = 'planos/form_plano.html'

    def get(self, request, pk):
        plano = get_object_or_404(Plano, pk=pk)
        return render(request, self.template_name, {
            'form':    PlanoForm(instance=plano),
            'usuario': request.user,
            'titulo':  f'Editar Plano — {plano.nome}',
        })

    def post(self, request, pk):
        plano = get_object_or_404(Plano, pk=pk)
        form  = PlanoForm(request.POST, instance=plano)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plano atualizado.')
            return redirect('planos:listar_planos')
        return render(request, self.template_name, {
            'form':    form,
            'usuario': request.user,
            'titulo':  f'Editar Plano — {plano.nome}',
        })


# ---------------------------------------------------------------------------
# Assinaturas
# ---------------------------------------------------------------------------

class ListarAssinaturasView(PlatformAdminRequiredMixin, View):
    template_name = 'planos/listar_assinaturas.html'

    def get(self, request):
        assinaturas = (
            AssinaturaEscola.objects
            .select_related('escola', 'plano', 'ativado_por')
            .order_by('escola__nome_escola')
        )
        return render(request, self.template_name, {
            'assinaturas': assinaturas,
            'usuario':     request.user,
        })


class DetalheAssinaturaView(PlatformAdminRequiredMixin, View):
    template_name = 'planos/detalhe_assinatura.html'

    def get(self, request, pk):
        assinatura = get_object_or_404(
            AssinaturaEscola.objects.select_related('escola', 'plano', 'ativado_por'),
            pk=pk,
        )
        historico = assinatura.historico.select_related('plano_anterior', 'plano_novo', 'alterado_por')
        modulos   = assinatura.modulos_escola.select_related('modulo')
        return render(request, self.template_name, {
            'assinatura': assinatura,
            'historico':  historico,
            'modulos':    modulos,
            'usuario':    request.user,
            'form_ativar':    AssinaturaAtivarForm(),
            'form_grace':     AssinaturaGraceForm(),
            'form_suspender': AssinaturaSuspenderForm(),
            'form_cancelar':  AssinaturaCancelarForm(),
        })


class AtivarAssinaturaView(PlatformAdminRequiredMixin, View):
    def post(self, request, pk):
        assinatura = get_object_or_404(AssinaturaEscola, pk=pk)
        form = AssinaturaAtivarForm(request.POST)
        if form.is_valid():
            assinatura_service.ativar(
                assinatura=assinatura,
                plano=form.cleaned_data['plano'],
                data_vencimento=form.cleaned_data['data_vencimento'],
                usuario=request.user,
                observacao=form.cleaned_data.get('observacao', ''),
            )
            messages.success(request, f'Assinatura de {assinatura.escola} ativada.')
        else:
            messages.error(request, 'Dados inválidos. Verifique o formulário.')
        return redirect('planos:detalhe_assinatura', pk=pk)


class IniciarGraceView(PlatformAdminRequiredMixin, View):
    def post(self, request, pk):
        assinatura = get_object_or_404(AssinaturaEscola, pk=pk)
        form = AssinaturaGraceForm(request.POST)
        if form.is_valid():
            assinatura_service.iniciar_grace(
                assinatura=assinatura,
                usuario=request.user,
                observacao=form.cleaned_data.get('observacao', ''),
            )
            messages.success(request, f'Carência iniciada para {assinatura.escola}.')
        return redirect('planos:detalhe_assinatura', pk=pk)


class SuspenderAssinaturaView(PlatformAdminRequiredMixin, View):
    def post(self, request, pk):
        assinatura = get_object_or_404(AssinaturaEscola, pk=pk)
        form = AssinaturaSuspenderForm(request.POST)
        if form.is_valid():
            assinatura_service.suspender(
                assinatura=assinatura,
                usuario=request.user,
                observacao=form.cleaned_data.get('observacao', ''),
            )
            messages.warning(request, f'Assinatura de {assinatura.escola} suspensa.')
        return redirect('planos:detalhe_assinatura', pk=pk)


class CancelarAssinaturaView(PlatformAdminRequiredMixin, View):
    def post(self, request, pk):
        assinatura = get_object_or_404(AssinaturaEscola, pk=pk)
        form = AssinaturaCancelarForm(request.POST)
        if form.is_valid():
            assinatura_service.cancelar(
                assinatura=assinatura,
                usuario=request.user,
                observacao=form.cleaned_data.get('observacao', ''),
            )
            messages.error(request, f'Assinatura de {assinatura.escola} cancelada.')
        return redirect('planos:detalhe_assinatura', pk=pk)
