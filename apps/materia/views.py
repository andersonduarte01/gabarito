from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.materia.models import Materia, MateriaSerieConfig
from .forms import MateriaForm, VincularSerieForm
from .services import materia_service


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


class ListarMateriasView(_LeituraMixin, View):
    template_name = 'materia/lista.html'

    def get(self, request):
        materias = (
            Materia.objects
            .filter(escola=request.escola)
            .order_by('nome')
        )
        return render(request, self.template_name, self._ctx(request, materias=materias))


class CriarMateriaView(_DiretorMixin, View):
    template_name = 'materia/form_materia.html'

    def get(self, request):
        return render(request, self.template_name, self._ctx(
            request, form=MateriaForm(), editando=False,
        ))

    def post(self, request):
        form = MateriaForm(request.POST)
        if form.is_valid():
            materia_service.criar(request.escola, form.cleaned_data)
            messages.success(request, 'Materia criada com sucesso.')
            return redirect('materia:lista')
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=False,
        ))


class EditarMateriaView(_DiretorMixin, View):
    template_name = 'materia/form_materia.html'

    def _get(self, request, pk):
        return get_object_or_404(Materia, pk=pk, escola=request.escola)

    def get(self, request, pk):
        materia = self._get(request, pk)
        return render(request, self.template_name, self._ctx(
            request, form=MateriaForm(instance=materia), editando=True, materia=materia,
        ))

    def post(self, request, pk):
        materia = self._get(request, pk)
        form = MateriaForm(request.POST, instance=materia)
        if form.is_valid():
            materia_service.editar(materia, form.cleaned_data)
            messages.success(request, 'Materia atualizada.')
            return redirect('materia:lista')
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, materia=materia,
        ))


class DesativarMateriaView(_DiretorMixin, View):
    def post(self, request, pk):
        materia = get_object_or_404(Materia, pk=pk, escola=request.escola)
        materia_service.desativar(materia)
        messages.success(request, 'Materia desativada.')
        return redirect('materia:lista')


class ReativarMateriaView(_DiretorMixin, View):
    def post(self, request, pk):
        materia = get_object_or_404(Materia, pk=pk, escola=request.escola)
        materia_service.reativar(materia)
        messages.success(request, 'Materia reativada.')
        return redirect('materia:lista')


class DetalheMateriaView(_LeituraMixin, View):
    template_name = 'materia/detalhe.html'

    def _get(self, request, pk):
        return get_object_or_404(Materia, pk=pk, escola=request.escola)

    def get(self, request, pk):
        materia       = self._get(request, pk)
        series_ativas = materia.series_config.filter(ativo=True).select_related('serie__segmento')
        form_vincular = VincularSerieForm(materia=materia, escola=request.escola)
        tem_series_disponiveis = form_vincular.fields['serie'].queryset.exists()
        return render(request, self.template_name, self._ctx(
            request,
            materia=materia,
            series_ativas=series_ativas,
            form_vincular=form_vincular,
            tem_series_disponiveis=tem_series_disponiveis,
        ))


class VincularSerieView(_DiretorMixin, View):
    def post(self, request, pk):
        materia = get_object_or_404(Materia, pk=pk, escola=request.escola)
        form    = VincularSerieForm(request.POST, materia=materia, escola=request.escola)
        if form.is_valid():
            materia_service.vincular_serie(materia, form.cleaned_data['serie'])
            messages.success(request, 'Serie vinculada.')
        else:
            messages.error(request, 'Selecione uma serie valida.')
        return redirect('materia:detalhe', pk=pk)


class DesvincularSerieView(_DiretorMixin, View):
    def post(self, request, pk, config_pk):
        get_object_or_404(Materia, pk=pk, escola=request.escola)
        config = get_object_or_404(MateriaSerieConfig, pk=config_pk, materia__escola=request.escola)
        materia_service.desvincular_serie(config)
        messages.success(request, 'Serie desvinculada.')
        return redirect('materia:detalhe', pk=pk)
