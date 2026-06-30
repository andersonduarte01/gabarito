from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views import View

from .models import AcaoAuditoria
from .services import auditoria_service


class _DiretorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo != 'DIRETOR':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel}


class LogAuditoriaView(_DiretorRequiredMixin, View):
    template_name = 'auditoria/lista.html'

    def get(self, request):
        filtros = {
            'acao':   request.GET.get('acao') or None,
            'modelo': request.GET.get('modelo') or None,
        }
        qs = auditoria_service.listar_escola(request.escola, filtros)
        paginator = Paginator(qs, 25)
        page_obj = paginator.get_page(request.GET.get('page'))
        return render(request, self.template_name, {
            **self._ctx(request),
            'page_obj': page_obj,
            'acoes':    AcaoAuditoria.choices,
            'filtros':  filtros,
            'active':   'auditoria',
        })
