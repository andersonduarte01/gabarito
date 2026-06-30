from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import AnoLetivoForm, PeriodoLetivoForm
from .models import AnoLetivo, PeriodoLetivo
from .services import ano_letivo_service
from .services.ano_letivo_service import AnoLetivoError

_PAPEIS_LEITURA = ('DIRETOR', 'FUNCIONARIO')


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


class _LeituraRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in _PAPEIS_LEITURA:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel}


class ListarAnoLetivoView(_LeituraRequiredMixin, View):
    template_name = 'ano_letivo/lista.html'

    def get(self, request):
        anos = AnoLetivo.objects.filter(escola=request.escola).prefetch_related('periodos')
        return render(request, self.template_name, {
            **self._ctx(request),
            'anos': anos,
            'active': 'ano_letivo',
            'eh_diretor': request.papel.tipo == 'DIRETOR',
        })


class CriarAnoLetivoView(_DiretorRequiredMixin, View):
    template_name = 'ano_letivo/form_ano.html'

    def get(self, request):
        return render(request, self.template_name, {
            **self._ctx(request),
            'form': AnoLetivoForm(),
            'active': 'ano_letivo',
        })

    def post(self, request):
        form = AnoLetivoForm(request.POST)
        if form.is_valid():
            try:
                ano = ano_letivo_service.criar(request.escola, form.cleaned_data, request.user)
                messages.success(request, f'Ano letivo {ano.ano} criado com sucesso.')
                return redirect('ano_letivo:detalhe', pk=ano.pk)
            except AnoLetivoError as e:
                messages.error(request, str(e))
        return render(request, self.template_name, {
            **self._ctx(request),
            'form': form,
            'active': 'ano_letivo',
        })


class DetalheAnoLetivoView(_LeituraRequiredMixin, View):
    template_name = 'ano_letivo/detalhe.html'

    def get(self, request, pk):
        ano = get_object_or_404(AnoLetivo, pk=pk, escola=request.escola)
        periodos = ano.periodos.all()
        return render(request, self.template_name, {
            **self._ctx(request),
            'ano': ano,
            'periodos': periodos,
            'active': 'ano_letivo',
            'eh_diretor': request.papel.tipo == 'DIRETOR',
        })


class IniciarAnoLetivoView(_DiretorRequiredMixin, View):
    def post(self, request, pk):
        ano = get_object_or_404(AnoLetivo, pk=pk, escola=request.escola)
        try:
            ano_letivo_service.iniciar(ano, request.user)
            messages.success(request, f'Ano letivo {ano.ano} iniciado.')
        except AnoLetivoError as e:
            messages.error(request, str(e))
        return redirect('ano_letivo:detalhe', pk=pk)


class EncerrarAnoLetivoView(_DiretorRequiredMixin, View):
    def post(self, request, pk):
        ano = get_object_or_404(AnoLetivo, pk=pk, escola=request.escola)
        try:
            ano_letivo_service.encerrar(ano, request.user)
            messages.success(request, f'Ano letivo {ano.ano} encerrado.')
        except AnoLetivoError as e:
            messages.error(request, str(e))
        return redirect('ano_letivo:detalhe', pk=pk)


class CriarPeriodoView(_DiretorRequiredMixin, View):
    template_name = 'ano_letivo/form_periodo.html'

    def get(self, request, pk):
        ano = get_object_or_404(AnoLetivo, pk=pk, escola=request.escola)
        return render(request, self.template_name, {
            **self._ctx(request),
            'form': PeriodoLetivoForm(),
            'ano': ano,
            'active': 'ano_letivo',
        })

    def post(self, request, pk):
        ano = get_object_or_404(AnoLetivo, pk=pk, escola=request.escola)
        form = PeriodoLetivoForm(request.POST)
        if form.is_valid():
            try:
                ano_letivo_service.criar_periodo(ano, form.cleaned_data)
                messages.success(request, 'Período criado.')
                return redirect('ano_letivo:detalhe', pk=pk)
            except AnoLetivoError as e:
                messages.error(request, str(e))
        return render(request, self.template_name, {
            **self._ctx(request),
            'form': form,
            'ano': ano,
            'active': 'ano_letivo',
        })


class EditarPeriodoView(_DiretorRequiredMixin, View):
    template_name = 'ano_letivo/form_periodo.html'

    def get(self, request, pk, periodo_pk):
        ano = get_object_or_404(AnoLetivo, pk=pk, escola=request.escola)
        periodo = get_object_or_404(PeriodoLetivo, pk=periodo_pk, ano_letivo=ano)
        form = PeriodoLetivoForm(initial={
            'numero':      periodo.numero,
            'nome':        periodo.nome,
            'data_inicio': periodo.data_inicio,
            'data_fim':    periodo.data_fim,
        })
        return render(request, self.template_name, {
            **self._ctx(request),
            'form': form,
            'ano': ano,
            'periodo': periodo,
            'active': 'ano_letivo',
        })

    def post(self, request, pk, periodo_pk):
        ano = get_object_or_404(AnoLetivo, pk=pk, escola=request.escola)
        periodo = get_object_or_404(PeriodoLetivo, pk=periodo_pk, ano_letivo=ano)
        form = PeriodoLetivoForm(request.POST)
        if form.is_valid():
            try:
                ano_letivo_service.editar_periodo(periodo, form.cleaned_data)
                messages.success(request, 'Período atualizado.')
                return redirect('ano_letivo:detalhe', pk=pk)
            except AnoLetivoError as e:
                messages.error(request, str(e))
        return render(request, self.template_name, {
            **self._ctx(request),
            'form': form,
            'ano': ano,
            'periodo': periodo,
            'active': 'ano_letivo',
        })


class RemoverPeriodoView(_DiretorRequiredMixin, View):
    def post(self, request, pk, periodo_pk):
        ano = get_object_or_404(AnoLetivo, pk=pk, escola=request.escola)
        periodo = get_object_or_404(PeriodoLetivo, pk=periodo_pk, ano_letivo=ano)
        try:
            ano_letivo_service.remover_periodo(periodo)
            messages.success(request, f'Período "{periodo.nome}" removido.')
        except AnoLetivoError as e:
            messages.error(request, str(e))
        return redirect('ano_letivo:detalhe', pk=pk)
