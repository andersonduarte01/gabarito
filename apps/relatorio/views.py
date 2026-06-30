from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from .forms import (
    FiltroBoletimLoteForm,
    FiltroEscolaPeriodoForm,
    FiltroFinanceiroForm,
    FiltroInadimplenciaForm,
    FiltroTurmaPeriodoForm,
)
from .services import relatorio_service


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


# ---------------------------------------------------------------------------
# Index — catálogo de relatórios
# ---------------------------------------------------------------------------

class IndexRelatoriosView(_LeituraMixin, View):
    template_name = 'relatorio/index.html'

    def get(self, request):
        from .models import RelatorioGerado
        recentes = RelatorioGerado.objects.filter(
            escola=request.escola
        ).order_by('-gerado_em')[:5]
        return render(request, self.template_name, self._ctx(request, recentes=recentes))


# ---------------------------------------------------------------------------
# Desempenho por turma
# ---------------------------------------------------------------------------

class DesempenhoTurmaView(_LeituraMixin, View):
    template_name = 'relatorio/desempenho_turma.html'

    def get(self, request):
        form = FiltroTurmaPeriodoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = FiltroTurmaPeriodoForm(request.escola, request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._ctx(request, form=form))

        turma          = form.cleaned_data['turma']
        periodo_letivo = form.cleaned_data['periodo_letivo']
        formato        = form.cleaned_data['formato']

        try:
            resultado = relatorio_service.gerar_desempenho_turma(turma, periodo_letivo, formato)
        except RuntimeError as e:
            messages.error(request, str(e))
            return render(request, self.template_name, self._ctx(request, form=form))

        if formato == 'xlsx':
            resp = HttpResponse(resultado, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            resp['Content-Disposition'] = f'attachment; filename="desempenho_{turma.nome}.xlsx"'
            return resp
        if formato == 'pdf':
            resp = HttpResponse(resultado, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="desempenho_{turma.nome}.pdf"'
            return resp

        return render(request, self.template_name, self._ctx(request, form=form, resultado=resultado))


# ---------------------------------------------------------------------------
# Frequência por turma
# ---------------------------------------------------------------------------

class FrequenciaTurmaView(_LeituraMixin, View):
    template_name = 'relatorio/frequencia_turma.html'

    def get(self, request):
        form = FiltroTurmaPeriodoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = FiltroTurmaPeriodoForm(request.escola, request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._ctx(request, form=form))

        turma   = form.cleaned_data['turma']
        periodo = form.cleaned_data['periodo_letivo']
        formato = form.cleaned_data['formato']

        try:
            resultado = relatorio_service.gerar_frequencia_turma(turma, periodo, formato)
        except RuntimeError as e:
            messages.error(request, str(e))
            return render(request, self.template_name, self._ctx(request, form=form))

        if formato == 'xlsx':
            resp = HttpResponse(resultado, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            resp['Content-Disposition'] = f'attachment; filename="frequencia_{turma.nome}.xlsx"'
            return resp
        if formato == 'pdf':
            resp = HttpResponse(resultado, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="frequencia_{turma.nome}.pdf"'
            return resp

        return render(request, self.template_name, self._ctx(request, form=form, resultado=resultado))


# ---------------------------------------------------------------------------
# Alunos em risco
# ---------------------------------------------------------------------------

class AlunosEmRiscoView(_LeituraMixin, View):
    template_name = 'relatorio/alunos_em_risco.html'

    def get(self, request):
        form = FiltroEscolaPeriodoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = FiltroEscolaPeriodoForm(request.escola, request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._ctx(request, form=form))

        periodo = form.cleaned_data['periodo_letivo']
        formato = form.cleaned_data['formato']

        try:
            resultado = relatorio_service.gerar_alunos_em_risco(request.escola, periodo, formato)
        except RuntimeError as e:
            messages.error(request, str(e))
            return render(request, self.template_name, self._ctx(request, form=form))

        if formato == 'xlsx':
            resp = HttpResponse(resultado, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            resp['Content-Disposition'] = 'attachment; filename="alunos_em_risco.xlsx"'
            return resp
        if formato == 'pdf':
            resp = HttpResponse(resultado, content_type='application/pdf')
            resp['Content-Disposition'] = 'attachment; filename="alunos_em_risco.pdf"'
            return resp

        return render(request, self.template_name, self._ctx(request, form=form, resultado=resultado))


# ---------------------------------------------------------------------------
# Boletim em lote
# ---------------------------------------------------------------------------

class BoletimLoteView(_LeituraMixin, View):
    template_name = 'relatorio/boletim_lote.html'

    def get(self, request):
        form = FiltroBoletimLoteForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = FiltroBoletimLoteForm(request.escola, request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._ctx(request, form=form))

        turma      = form.cleaned_data['turma']
        ano_letivo = form.cleaned_data['ano_letivo']

        try:
            resultado = relatorio_service.gerar_boletim_lote(turma, ano_letivo, 'pdf')
        except RuntimeError as e:
            messages.error(request, str(e))
            return render(request, self.template_name, self._ctx(request, form=form))

        resp = HttpResponse(resultado, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="boletim_lote_{turma.nome}_{ano_letivo.ano}.pdf"'
        return resp


# ---------------------------------------------------------------------------
# Desempenho por professor (DIRETOR only)
# ---------------------------------------------------------------------------

class DesempenhoProfessorView(_DiretorMixin, View):
    template_name = 'relatorio/desempenho_professor.html'

    def get(self, request):
        form = FiltroEscolaPeriodoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = FiltroEscolaPeriodoForm(request.escola, request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._ctx(request, form=form))

        periodo = form.cleaned_data['periodo_letivo']
        formato = form.cleaned_data['formato']

        try:
            resultado = relatorio_service.gerar_desempenho_professor(request.escola, periodo, formato)
        except RuntimeError as e:
            messages.error(request, str(e))
            return render(request, self.template_name, self._ctx(request, form=form))

        if formato == 'xlsx':
            resp = HttpResponse(resultado, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            resp['Content-Disposition'] = 'attachment; filename="desempenho_professor.xlsx"'
            return resp
        if formato == 'pdf':
            resp = HttpResponse(resultado, content_type='application/pdf')
            resp['Content-Disposition'] = 'attachment; filename="desempenho_professor.pdf"'
            return resp

        return render(request, self.template_name, self._ctx(request, form=form, resultado=resultado))


# ---------------------------------------------------------------------------
# Inadimplência
# ---------------------------------------------------------------------------

class InadimplenciaView(_LeituraMixin, View):
    template_name = 'relatorio/inadimplencia.html'

    def get(self, request):
        form = FiltroInadimplenciaForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = FiltroInadimplenciaForm(request.escola, request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._ctx(request, form=form))

        formato = form.cleaned_data['formato']
        try:
            resultado = relatorio_service.gerar_inadimplencia(
                escola=request.escola,
                data_inicio=form.cleaned_data.get('data_inicio'),
                data_fim=form.cleaned_data.get('data_fim'),
                turma=form.cleaned_data.get('turma'),
                formato=formato,
            )
        except RuntimeError as e:
            messages.error(request, str(e))
            return render(request, self.template_name, self._ctx(request, form=form))

        if formato == 'xlsx':
            resp = HttpResponse(resultado, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            resp['Content-Disposition'] = 'attachment; filename="inadimplencia.xlsx"'
            return resp
        if formato == 'pdf':
            resp = HttpResponse(resultado, content_type='application/pdf')
            resp['Content-Disposition'] = 'attachment; filename="inadimplencia.pdf"'
            return resp

        return render(request, self.template_name, self._ctx(request, form=form, resultado=resultado))


# ---------------------------------------------------------------------------
# Extrato financeiro
# ---------------------------------------------------------------------------

class ExtratoFinanceiroView(_LeituraMixin, View):
    template_name = 'relatorio/extrato_financeiro.html'

    def get(self, request):
        form = FiltroFinanceiroForm()
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = FiltroFinanceiroForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._ctx(request, form=form))

        formato = form.cleaned_data['formato']
        try:
            resultado = relatorio_service.gerar_extrato_financeiro(
                escola=request.escola,
                data_inicio=form.cleaned_data['data_inicio'],
                data_fim=form.cleaned_data['data_fim'],
                formato=formato,
            )
        except RuntimeError as e:
            messages.error(request, str(e))
            return render(request, self.template_name, self._ctx(request, form=form))

        if formato == 'xlsx':
            resp = HttpResponse(resultado, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            resp['Content-Disposition'] = 'attachment; filename="extrato_financeiro.xlsx"'
            return resp
        if formato == 'pdf':
            resp = HttpResponse(resultado, content_type='application/pdf')
            resp['Content-Disposition'] = 'attachment; filename="extrato_financeiro.pdf"'
            return resp

        return render(request, self.template_name, self._ctx(request, form=form, resultado=resultado))
