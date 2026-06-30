from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import ComunicadoForm
from .models import Comunicado
from .services import comunicado_service


class _LeituraMixin:
    PAPEIS_PERMITIDOS = ('DIRETOR', 'FUNCIONARIO', 'PROFESSOR')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in self.PAPEIS_PERMITIDOS:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class _GestorMixin:
    """DIRETOR e COLABORADOR podem criar/publicar/excluir; PROFESSOR pode criar apenas."""
    PAPEIS_PERMITIDOS = ('DIRETOR', 'FUNCIONARIO', 'PROFESSOR')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in self.PAPEIS_PERMITIDOS:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


# ---------------------------------------------------------------------------
# Lista
# ---------------------------------------------------------------------------

class ListarComunicadosView(_LeituraMixin, View):
    template_name = 'comunicado/lista.html'

    def get(self, request):
        escola = request.escola
        qs = Comunicado.objects.filter(escola=escola).prefetch_related('turmas')

        tipo   = request.GET.get('tipo', '')
        status = request.GET.get('status', '')

        if tipo:
            qs = qs.filter(tipo=tipo)
        if status == 'publicado':
            qs = qs.filter(publicada=True)
        elif status == 'rascunho':
            qs = qs.filter(publicada=False)

        paginator = Paginator(qs, 20)
        page      = paginator.get_page(request.GET.get('page'))

        return render(request, self.template_name, self._ctx(
            request,
            page=page,
            tipo_filtro=tipo,
            status_filtro=status,
            tipos=Comunicado._meta.get_field('tipo').choices,
        ))


# ---------------------------------------------------------------------------
# Criar
# ---------------------------------------------------------------------------

class CriarComunicadoView(_GestorMixin, View):
    template_name = 'comunicado/form_comunicado.html'

    def get(self, request):
        form = ComunicadoForm(escola=request.escola, papel=request.papel)
        return render(request, self.template_name, self._ctx(request, form=form, acao='Novo Comunicado'))

    def post(self, request):
        form = ComunicadoForm(request.escola, request.papel, request.POST)
        if form.is_valid():
            dados = form.cleaned_data.copy()
            turmas = dados.pop('turmas')
            dados['turmas'] = list(turmas)
            comunicado = comunicado_service.criar(request.escola, request.user, dados)
            messages.success(request, 'Comunicado criado como rascunho.')
            return redirect('comunicado:detalhe', pk=comunicado.pk)
        return render(request, self.template_name, self._ctx(request, form=form, acao='Novo Comunicado'))


# ---------------------------------------------------------------------------
# Detalhe
# ---------------------------------------------------------------------------

class DetalheComunicadoView(_LeituraMixin, View):
    template_name = 'comunicado/detalhe.html'

    def get(self, request, pk):
        comunicado = get_object_or_404(Comunicado, pk=pk, escola=request.escola)
        if comunicado.publicada:
            comunicado_service.registrar_leitura(comunicado, request.user)
        leituras = comunicado.leituras.select_related('usuario').order_by('-lido_em')
        return render(request, self.template_name, self._ctx(
            request,
            comunicado=comunicado,
            leituras=leituras,
            total_leituras=leituras.count(),
        ))


# ---------------------------------------------------------------------------
# Editar
# ---------------------------------------------------------------------------

class EditarComunicadoView(_GestorMixin, View):
    template_name = 'comunicado/form_comunicado.html'

    def _get_comunicado(self, request, pk):
        comunicado = get_object_or_404(Comunicado, pk=pk, escola=request.escola)
        papel = request.papel
        # Professor só edita próprio comunicado; Diretor edita qualquer um
        if papel.tipo == 'PROFESSOR' and comunicado.autor != request.user:
            raise PermissionDenied
        return comunicado

    def get(self, request, pk):
        comunicado = self._get_comunicado(request, pk)
        form = ComunicadoForm(
            escola=request.escola, papel=request.papel,
            instance=comunicado,
        )
        return render(request, self.template_name, self._ctx(
            request, form=form, acao='Editar Comunicado', comunicado=comunicado
        ))

    def post(self, request, pk):
        comunicado = self._get_comunicado(request, pk)
        form = ComunicadoForm(
            request.escola, request.papel,
            request.POST, instance=comunicado,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Comunicado atualizado.')
            return redirect('comunicado:detalhe', pk=comunicado.pk)
        return render(request, self.template_name, self._ctx(
            request, form=form, acao='Editar Comunicado', comunicado=comunicado
        ))


# ---------------------------------------------------------------------------
# Publicar / Despublicar
# ---------------------------------------------------------------------------

class PublicarComunicadoView(_GestorMixin, View):
    def post(self, request, pk):
        comunicado = get_object_or_404(Comunicado, pk=pk, escola=request.escola)
        papel = request.papel
        if papel.tipo == 'PROFESSOR' and comunicado.autor != request.user:
            raise PermissionDenied
        comunicado_service.publicar(comunicado)
        messages.success(request, 'Comunicado publicado e destinatários notificados.')
        return redirect('comunicado:detalhe', pk=comunicado.pk)


class DespublicarComunicadoView(_GestorMixin, View):
    def post(self, request, pk):
        papel = request.papel
        if papel.tipo not in ('DIRETOR', 'FUNCIONARIO'):
            raise PermissionDenied
        comunicado = get_object_or_404(Comunicado, pk=pk, escola=request.escola)
        comunicado.publicada = False
        comunicado.save(update_fields=['publicada'])
        messages.success(request, 'Comunicado despublicado.')
        return redirect('comunicado:detalhe', pk=comunicado.pk)


# ---------------------------------------------------------------------------
# Excluir
# ---------------------------------------------------------------------------

class ExcluirComunicadoView(_GestorMixin, View):
    def post(self, request, pk):
        comunicado = get_object_or_404(Comunicado, pk=pk, escola=request.escola)
        papel = request.papel
        if papel.tipo == 'PROFESSOR' and comunicado.autor != request.user:
            raise PermissionDenied
        if papel.tipo not in ('DIRETOR', 'FUNCIONARIO') and comunicado.autor != request.user:
            raise PermissionDenied
        comunicado.delete()
        messages.success(request, 'Comunicado excluído.')
        return redirect('comunicado:lista')
