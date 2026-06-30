from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import Notificacao
from .services import notificacao_service


class _AuthMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request):
        return {'usuario': request.user, 'escola': getattr(request, 'escola', None), 'papel': getattr(request, 'papel', None)}


class ListarNotificacoesView(_AuthMixin, View):
    template_name = 'notificacao/lista.html'

    def get(self, request):
        qs = notificacao_service.listar_todas(request.user)
        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(request.GET.get('page'))
        return render(request, self.template_name, {
            **self._ctx(request),
            'page_obj': page_obj,
            'active': 'notificacoes',
        })


class MarcarLidaView(_AuthMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(Notificacao, pk=pk, destinatario=request.user)
        notificacao_service.marcar_lida(notif)
        return redirect('notificacao:lista')


class MarcarTodasLidasView(_AuthMixin, View):
    def post(self, request):
        notificacao_service.marcar_todas_lidas(request.user)
        messages.success(request, 'Todas as notificações foram marcadas como lidas.')
        return redirect('notificacao:lista')
