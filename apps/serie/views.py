from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.serie.models import Serie
from .forms import CriarSerieForm, EditarSerieForm
from .services import serie_service


class _LeituraMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in ('DIRETOR', 'FUNCIONARIO'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class _DiretorMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo != 'DIRETOR':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class ListarSeriesView(_LeituraMixin, View):
    template_name = 'serie/lista.html'

    def get(self, request):
        escola    = request.escola
        segmentos = escola.segmentos.all().order_by('tipo')
        dados = []
        for segmento in segmentos:
            series_list = list(segmento.series.all().order_by('ordem', 'nome'))
            dados.append({
                'segmento': segmento,
                'series':   series_list,
                'total':    len(series_list),
            })
        return render(request, self.template_name, self._ctx(request, dados=dados))


class CriarSerieView(_DiretorMixin, View):
    template_name = 'serie/form_serie.html'

    def get(self, request):
        form = CriarSerieForm(escola=request.escola)
        segmento_pk = request.GET.get('segmento')
        if segmento_pk:
            form.fields['segmento'].initial = segmento_pk
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=False,
        ))

    def post(self, request):
        form = CriarSerieForm(request.POST, escola=request.escola)
        if form.is_valid():
            segmento = form.cleaned_data['segmento']
            nome     = form.cleaned_data['nome']
            ordem    = form.cleaned_data['ordem']
            serie_service.criar(request.escola, segmento, {'nome': nome, 'ordem': ordem})
            messages.success(request, 'Série criada com sucesso.')
            return redirect('serie:lista')
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=False,
        ))


class EditarSerieView(_DiretorMixin, View):
    template_name = 'serie/form_serie.html'

    def _get_serie(self, request, pk):
        return get_object_or_404(Serie, pk=pk, escola=request.escola)

    def get(self, request, pk):
        serie = self._get_serie(request, pk)
        form  = EditarSerieForm(instance=serie)
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, serie=serie,
        ))

    def post(self, request, pk):
        serie = self._get_serie(request, pk)
        form  = EditarSerieForm(request.POST, instance=serie)
        if form.is_valid():
            serie_service.editar(serie, form.cleaned_data)
            messages.success(request, 'Serie atualizada.')
            return redirect('serie:lista')
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, serie=serie,
        ))


class DesativarSerieView(_DiretorMixin, View):
    def post(self, request, pk):
        serie = get_object_or_404(Serie, pk=pk, escola=request.escola)
        serie_service.desativar(serie)
        messages.success(request, 'Serie desativada.')
        return redirect('serie:lista')


class ReativarSerieView(_DiretorMixin, View):
    def post(self, request, pk):
        serie = get_object_or_404(Serie, pk=pk, escola=request.escola)
        serie_service.reativar(serie)
        messages.success(request, 'Serie reativada.')
        return redirect('serie:lista')
