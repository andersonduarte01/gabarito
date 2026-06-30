from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import EventoForm
from .models import Evento
from .services import evento_service


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
    PAPEIS_PERMITIDOS = ('DIRETOR', 'FUNCIONARIO')

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
# Lista / Calendário
# ---------------------------------------------------------------------------

class ListarEventosView(_LeituraMixin, View):
    template_name = 'agenda/lista.html'

    def get(self, request):
        escola = request.escola
        qs = Evento.objects.filter(escola=escola).prefetch_related('turmas')

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
            tipos=Evento._meta.get_field('tipo').choices,
        ))


# ---------------------------------------------------------------------------
# Criar
# ---------------------------------------------------------------------------

class CriarEventoView(_GestorMixin, View):
    template_name = 'agenda/form_evento.html'

    def get(self, request):
        form = EventoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form, acao='Novo Evento'))

    def post(self, request):
        form = EventoForm(request.escola, request.POST)
        if form.is_valid():
            dados = form.cleaned_data.copy()
            turmas = dados.pop('turmas')
            dados['turmas'] = list(turmas)
            evento = evento_service.criar(request.escola, request.user, dados)
            messages.success(request, 'Evento criado como rascunho.')
            return redirect('agenda:detalhe', pk=evento.pk)
        return render(request, self.template_name, self._ctx(request, form=form, acao='Novo Evento'))


# ---------------------------------------------------------------------------
# Detalhe
# ---------------------------------------------------------------------------

class DetalheEventoView(_LeituraMixin, View):
    template_name = 'agenda/detalhe.html'

    def get(self, request, pk):
        evento = get_object_or_404(Evento, pk=pk, escola=request.escola)
        if evento.publicada:
            evento_service.registrar_leitura(evento, request.user)
        leituras = evento.leituras.select_related('usuario').order_by('-lido_em')
        return render(request, self.template_name, self._ctx(
            request,
            evento=evento,
            leituras=leituras,
            total_leituras=leituras.count(),
        ))


# ---------------------------------------------------------------------------
# Editar
# ---------------------------------------------------------------------------

class EditarEventoView(_GestorMixin, View):
    template_name = 'agenda/form_evento.html'

    def get(self, request, pk):
        evento = get_object_or_404(Evento, pk=pk, escola=request.escola)
        form = EventoForm(escola=request.escola, instance=evento)
        return render(request, self.template_name, self._ctx(
            request, form=form, acao='Editar Evento', evento=evento
        ))

    def post(self, request, pk):
        evento = get_object_or_404(Evento, pk=pk, escola=request.escola)
        form = EventoForm(request.escola, request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado.')
            return redirect('agenda:detalhe', pk=evento.pk)
        return render(request, self.template_name, self._ctx(
            request, form=form, acao='Editar Evento', evento=evento
        ))


# ---------------------------------------------------------------------------
# Publicar / Despublicar
# ---------------------------------------------------------------------------

class PublicarEventoView(_GestorMixin, View):
    def post(self, request, pk):
        evento = get_object_or_404(Evento, pk=pk, escola=request.escola)
        evento_service.publicar(evento)
        messages.success(request, 'Evento publicado e destinatários notificados.')
        return redirect('agenda:detalhe', pk=evento.pk)


class DespublicarEventoView(_GestorMixin, View):
    def post(self, request, pk):
        evento = get_object_or_404(Evento, pk=pk, escola=request.escola)
        evento.publicada = False
        evento.save(update_fields=['publicada'])
        messages.success(request, 'Evento despublicado.')
        return redirect('agenda:detalhe', pk=evento.pk)


# ---------------------------------------------------------------------------
# Excluir
# ---------------------------------------------------------------------------

class ExcluirEventoView(_GestorMixin, View):
    def post(self, request, pk):
        evento = get_object_or_404(Evento, pk=pk, escola=request.escola)
        evento.delete()
        messages.success(request, 'Evento excluído.')
        return redirect('agenda:lista')
