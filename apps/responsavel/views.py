from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import CriarResponsavelForm, CriarSemAcessoForm, EditarResponsavelForm, VincularAlunoForm
from .models import PerfilResponsavel, VinculoResponsavelAluno
from .services import responsavel_service


_ESCRITA = ('DIRETOR', 'FUNCIONARIO')
_LEITURA = ('DIRETOR', 'FUNCIONARIO')


class _LeituraMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in _LEITURA:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class _EscritaMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in _ESCRITA:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class ListarResponsaveisView(_LeituraMixin, View):
    template_name = 'responsavel/lista.html'

    def get(self, request):
        from django.db.models import Q
        escola = request.escola
        responsaveis = (
            PerfilResponsavel.objects
            .filter(Q(escola=escola) | Q(vinculos_aluno__aluno__escola=escola))
            .distinct()
            .prefetch_related('vinculos_aluno__aluno')
            .order_by('nome')
        )
        return render(request, self.template_name, self._ctx(request, responsaveis=responsaveis))


class CriarResponsavelView(_EscritaMixin, View):
    template_name = 'responsavel/form_responsavel.html'

    def get(self, request):
        tipo = request.GET.get('tipo', 'acesso')
        form_cls = CriarResponsavelForm if tipo == 'acesso' else CriarSemAcessoForm
        form = form_cls(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form, tipo=tipo))

    def post(self, request):
        tipo = request.POST.get('tipo', 'acesso')
        form_cls = CriarResponsavelForm if tipo == 'acesso' else CriarSemAcessoForm
        form = form_cls(request.POST, request.FILES, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                _campos_vinculo = {'aluno', 'parentesco', 'responsavel_principal', 'responsavel_financeiro'}
                if tipo == 'acesso':
                    perfil_dados = {
                        k: v for k, v in cd.items()
                        if k not in ('nome', 'email', 'senha', 'confirmar_senha') | _campos_vinculo
                    }
                    perfil = responsavel_service.criar(
                        escola=request.escola,
                        usuario_dados={'nome': cd['nome'], 'email': cd['email'], 'senha': cd.get('senha')},
                        perfil_dados=perfil_dados,
                    )
                else:
                    perfil_dados = {k: v for k, v in cd.items() if k not in _campos_vinculo}
                    perfil = responsavel_service.criar_sem_acesso(
                        escola=request.escola, perfil_dados=perfil_dados,
                    )
                if cd.get('aluno') and cd.get('parentesco'):
                    responsavel_service.vincular_aluno(
                        perfil=perfil,
                        aluno=cd['aluno'],
                        dados={
                            'parentesco':             cd['parentesco'],
                            'responsavel_principal':  cd.get('responsavel_principal', False),
                            'responsavel_financeiro': cd.get('responsavel_financeiro', False),
                        },
                    )
                messages.success(request, f'Responsável {cd["nome"]} cadastrado com sucesso.')
                return redirect('responsavel:detalhe', pk=perfil.pk)
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        return render(request, self.template_name, self._ctx(request, form=form, tipo=tipo))


class DetalheResponsavelView(_LeituraMixin, View):
    template_name = 'responsavel/detalhe.html'

    def get(self, request, pk):
        from django.db.models import Q
        responsavel = get_object_or_404(
            PerfilResponsavel.objects.prefetch_related('vinculos_aluno__aluno'),
            Q(escola=request.escola) | Q(vinculos_aluno__aluno__escola=request.escola),
            pk=pk,
        )
        vinculo_form = VincularAlunoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(
            request, responsavel=responsavel, vinculo_form=vinculo_form,
        ))


class EditarResponsavelView(_EscritaMixin, View):
    template_name = 'responsavel/form_responsavel.html'

    def _get(self, request, pk):
        from django.db.models import Q
        return get_object_or_404(
            PerfilResponsavel,
            Q(escola=request.escola) | Q(vinculos_aluno__aluno__escola=request.escola),
            pk=pk,
        )

    def get(self, request, pk):
        responsavel = self._get(request, pk)
        form = EditarResponsavelForm(instance=responsavel)
        return render(request, self.template_name, self._ctx(
            request, form=form, tipo='editar', responsavel=responsavel,
        ))

    def post(self, request, pk):
        responsavel = self._get(request, pk)
        form = EditarResponsavelForm(request.POST, request.FILES, instance=responsavel)
        if form.is_valid():
            responsavel_service.editar(responsavel, form.cleaned_data)
            messages.success(request, 'Responsável atualizado.')
            return redirect('responsavel:detalhe', pk=responsavel.pk)
        return render(request, self.template_name, self._ctx(
            request, form=form, tipo='editar', responsavel=responsavel,
        ))


class VincularAlunoView(_EscritaMixin, View):
    def post(self, request, pk):
        from django.db.models import Q
        responsavel = get_object_or_404(
            PerfilResponsavel,
            Q(escola=request.escola) | Q(vinculos_aluno__aluno__escola=request.escola),
            pk=pk,
        )
        form = VincularAlunoForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                responsavel_service.vincular_aluno(
                    perfil=responsavel,
                    aluno=cd['aluno'],
                    dados={
                        'parentesco':             cd['parentesco'],
                        'responsavel_principal':  cd['responsavel_principal'],
                        'responsavel_financeiro': cd['responsavel_financeiro'],
                    },
                )
                messages.success(request, f'Aluno {cd["aluno"].nome_completo} vinculado.')
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        else:
            messages.error(request, 'Dados inválidos.')
        return redirect('responsavel:detalhe', pk=responsavel.pk)


class DesvincularAlunoView(_EscritaMixin, View):
    def post(self, request, pk, vinculo_pk):
        from django.db.models import Q
        responsavel = get_object_or_404(
            PerfilResponsavel,
            Q(escola=request.escola) | Q(vinculos_aluno__aluno__escola=request.escola),
            pk=pk,
        )
        vinculo = get_object_or_404(VinculoResponsavelAluno, pk=vinculo_pk, responsavel=responsavel)
        responsavel_service.desvincular_aluno(vinculo)
        messages.success(request, 'Vínculo removido.')
        return redirect('responsavel:detalhe', pk=responsavel.pk)


# ---------------------------------------------------------------------------
# Portal do Responsável
# ---------------------------------------------------------------------------

class _ResponsavelMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo != 'RESPONSAVEL':
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class DashboardResponsavelView(_ResponsavelMixin, View):
    template_name = 'responsavel/portal_dashboard.html'

    def get(self, request):
        from apps.comunicado.models import Comunicado
        from apps.agenda.models import Evento
        from apps.boletim.models import SituacaoPeriodo
        import datetime

        try:
            perfil = request.user.perfil_responsavel
        except Exception:
            perfil = None

        filhos_data = []
        total_alertas = 0

        if perfil:
            vinculos = (
                perfil.vinculos_aluno
                .filter(ativo=True)
                .select_related('aluno')
            )
            for v in vinculos:
                aluno = v.aluno
                matricula = (
                    aluno.matriculas
                    .filter(ativo=True)
                    .select_related('turma__serie', 'ano_letivo')
                    .first()
                )
                alertas = 0
                if matricula:
                    alertas = aluno.resultados_periodo.filter(
                        ano_letivo=matricula.ano_letivo,
                        situacao_periodo__in=[
                            SituacaoPeriodo.RECUPERACAO,
                            SituacaoPeriodo.REPROVADO,
                        ],
                    ).count()
                total_alertas += alertas
                filhos_data.append({
                    'vinculo':   v,
                    'aluno':     aluno,
                    'matricula': matricula,
                    'alertas':   alertas,
                })

        comunicados_recentes = (
            Comunicado.objects
            .filter(escola=request.escola, publicada=True)
            .order_by('-criado_em')[:5]
        )
        proximos_eventos = (
            Evento.objects
            .filter(escola=request.escola, data_inicio__gte=datetime.date.today())
            .order_by('data_inicio', 'hora_inicio')[:5]
        )

        return render(request, self.template_name, self._ctx(
            request,
            active_nav='dashboard',
            perfil=perfil,
            filhos_data=filhos_data,
            total_alertas=total_alertas,
            comunicados_recentes=comunicados_recentes,
            proximos_eventos=proximos_eventos,
        ))


class PerfilResponsavelView(_ResponsavelMixin, View):
    template_name = 'responsavel/portal_perfil.html'

    def get(self, request):
        try:
            perfil = request.user.perfil_responsavel
        except Exception:
            perfil = None

        return render(request, self.template_name, self._ctx(
            request,
            active_nav='perfil',
            perfil=perfil,
        ))
