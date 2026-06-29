from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import (
    CobrancaAlunoForm,
    GerarCobrancasEscolaForm,
    GerarCobrancasTurmaForm,
    PlanoFinanceiroForm,
)
from .models import CobrancaAluno, PlanoFinanceiro, StatusCobranca
from .services import financeiro_service


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
# Dashboard
# ---------------------------------------------------------------------------

class DashboardFinanceiroView(_LeituraMixin, View):
    template_name = 'financeiro/dashboard.html'

    def get(self, request):
        escola = request.escola
        qs = CobrancaAluno.objects.filter(aluno__escola=escola)

        total     = qs.count()
        pendentes = qs.filter(status=StatusCobranca.PENDENTE).count()
        vencidos  = qs.filter(status=StatusCobranca.VENCIDO).count()
        pagos     = qs.filter(status=StatusCobranca.PAGO).count()

        recentes = (
            qs.select_related('aluno', 'plano_financeiro')
            .order_by('-criado_em')[:10]
        )

        return render(request, self.template_name, self._ctx(
            request,
            total=total,
            pendentes=pendentes,
            vencidos=vencidos,
            pagos=pagos,
            recentes=recentes,
        ))


# ---------------------------------------------------------------------------
# Cobranças
# ---------------------------------------------------------------------------

class ListarCobrancasView(_LeituraMixin, View):
    template_name = 'financeiro/lista_cobrancas.html'

    def get(self, request):
        escola = request.escola
        qs = (
            CobrancaAluno.objects
            .filter(aluno__escola=escola)
            .select_related('aluno', 'responsavel_financeiro', 'plano_financeiro')
            .order_by('-vencimento', '-criado_em')
        )
        status_f = request.GET.get('status', '')
        if status_f:
            qs = qs.filter(status=status_f)

        return render(request, self.template_name, self._ctx(
            request,
            cobrancas=qs,
            status_choices=StatusCobranca.choices,
            filtros={'status': status_f},
        ))


class DetalheCobrancaView(_LeituraMixin, View):
    template_name = 'financeiro/detalhe_cobranca.html'

    def get(self, request, pk):
        cobranca = self._get(request, pk)
        return render(request, self.template_name, self._ctx(request, cobranca=cobranca))

    def _get(self, request, pk):
        return get_object_or_404(
            CobrancaAluno.objects.select_related(
                'aluno', 'responsavel_financeiro', 'plano_financeiro', 'criado_por',
            ),
            pk=pk,
            aluno__escola=request.escola,
        )


class CriarCobrancaView(_LeituraMixin, View):
    template_name = 'financeiro/form_cobranca.html'

    def get(self, request):
        from apps.aluno.models import Aluno
        aluno_id = request.GET.get('aluno')
        aluno = None
        if aluno_id:
            aluno = get_object_or_404(Aluno, pk=aluno_id)
        form = CobrancaAlunoForm(escola=request.escola)
        alunos = (
            Aluno.objects
            .filter(matriculas__turma__escola=request.escola, ativo=True)
            .distinct()
            .order_by('nome_completo')
        )
        return render(request, self.template_name, self._ctx(
            request, form=form, alunos=alunos, aluno_pre=aluno,
        ))

    def post(self, request):
        from apps.aluno.models import Aluno
        form = CobrancaAlunoForm(request.POST, escola=request.escola)
        alunos = (
            Aluno.objects
            .filter(matriculas__turma__escola=request.escola, ativo=True)
            .distinct()
            .order_by('nome_completo')
        )
        if form.is_valid():
            cd = form.cleaned_data
            aluno_id = request.POST.get('aluno_id')
            aluno = get_object_or_404(Aluno, pk=aluno_id)
            try:
                cobranca = financeiro_service.gerar_cobranca_aluno(
                    aluno=aluno,
                    dados={
                        'descricao':        cd['descricao'],
                        'valor':            cd['valor'],
                        'vencimento':       cd['vencimento'],
                        'plano_financeiro': cd.get('plano_financeiro'),
                        'gateway':          cd['gateway'],
                    },
                    criado_por=request.user,
                )
                messages.success(request, 'Cobrança gerada com sucesso.')
                return redirect('financeiro:detalhe_cobranca', pk=cobranca.pk)
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        return render(request, self.template_name, self._ctx(
            request, form=form, alunos=alunos, aluno_pre=None,
        ))


class PagarManualView(_LeituraMixin, View):
    def post(self, request, pk):
        cobranca = get_object_or_404(
            CobrancaAluno,
            pk=pk,
            aluno__escola=request.escola,
        )
        try:
            financeiro_service.registrar_pagamento_manual(cobranca, request.user)
            messages.success(request, 'Pagamento registrado.')
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect('financeiro:detalhe_cobranca', pk=pk)


class CancelarCobrancaView(_DiretorMixin, View):
    def post(self, request, pk):
        cobranca = get_object_or_404(
            CobrancaAluno,
            pk=pk,
            aluno__escola=request.escola,
        )
        try:
            financeiro_service.cancelar(cobranca, request.user)
            messages.success(request, 'Cobrança cancelada.')
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect('financeiro:detalhe_cobranca', pk=pk)


# ---------------------------------------------------------------------------
# Geração em massa
# ---------------------------------------------------------------------------

class GerarPorTurmaView(_LeituraMixin, View):
    template_name = 'financeiro/gerar_turma.html'

    def get(self, request):
        form = GerarCobrancasTurmaForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = GerarCobrancasTurmaForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                count = financeiro_service.gerar_cobrancas_turma(
                    turma=cd['turma'],
                    plano=cd['plano_financeiro'],
                    vencimento=cd['vencimento'],
                    criado_por=request.user,
                )
                messages.success(request, f'{count} cobranças geradas para a turma.')
                return redirect('financeiro:lista_cobrancas')
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        return render(request, self.template_name, self._ctx(request, form=form))


class GerarPorEscolaView(_LeituraMixin, View):
    template_name = 'financeiro/gerar_escola.html'

    def get(self, request):
        form = GerarCobrancasEscolaForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = GerarCobrancasEscolaForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                count = financeiro_service.gerar_cobrancas_escola(
                    escola=request.escola,
                    plano=cd['plano_financeiro'],
                    vencimento=cd['vencimento'],
                    criado_por=request.user,
                )
                messages.success(request, f'{count} cobranças geradas para toda a escola.')
                return redirect('financeiro:lista_cobrancas')
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        return render(request, self.template_name, self._ctx(request, form=form))


# ---------------------------------------------------------------------------
# Planos Financeiros
# ---------------------------------------------------------------------------

class ListarPlanosView(_DiretorMixin, View):
    template_name = 'financeiro/lista_planos.html'

    def get(self, request):
        planos = PlanoFinanceiro.objects.filter(escola=request.escola).order_by('nome')
        return render(request, self.template_name, self._ctx(request, planos=planos))


class CriarPlanoView(_DiretorMixin, View):
    template_name = 'financeiro/form_plano.html'

    def get(self, request):
        form = PlanoFinanceiroForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))

    def post(self, request):
        form = PlanoFinanceiroForm(request.POST, escola=request.escola)
        if form.is_valid():
            plano = form.save(commit=False)
            plano.escola = request.escola
            plano.save()
            messages.success(request, 'Plano financeiro criado.')
            return redirect('financeiro:lista_planos')
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))


class EditarPlanoView(_DiretorMixin, View):
    template_name = 'financeiro/form_plano.html'

    def _get(self, request, pk):
        return get_object_or_404(PlanoFinanceiro, pk=pk, escola=request.escola)

    def get(self, request, pk):
        plano = self._get(request, pk)
        form  = PlanoFinanceiroForm(instance=plano, escola=request.escola)
        return render(request, self.template_name, self._ctx(
            request, form=form, plano=plano, editando=True,
        ))

    def post(self, request, pk):
        plano = self._get(request, pk)
        form  = PlanoFinanceiroForm(request.POST, instance=plano, escola=request.escola)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plano atualizado.')
            return redirect('financeiro:lista_planos')
        return render(request, self.template_name, self._ctx(
            request, form=form, plano=plano, editando=True,
        ))


# ---------------------------------------------------------------------------
# Webhook stub
# ---------------------------------------------------------------------------

class WebhookMercadoPagoView(View):
    def post(self, request):
        import json
        try:
            payload = json.loads(request.body)
        except Exception:
            return JsonResponse({'erro': 'payload inválido'}, status=400)
        financeiro_service.processar_webhook('MERCADO_PAGO', payload)
        return JsonResponse({'ok': True})
