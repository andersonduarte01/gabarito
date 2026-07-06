from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import AtivarAcessoForm, CriarAlunoForm, EditarAlunoForm, MatriculaTurmaForm, TrocarTurmaForm, VincularResponsavelForm
from .models import Aluno, MatriculaTurma
from .services import aluno_service

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


class ListarAlunosView(_LeituraMixin, View):
    template_name = 'aluno/lista.html'

    def get(self, request):
        escola = request.escola
        qs = (
            Aluno.objects
            .filter(escola=escola)
            .prefetch_related('matriculas__turma', 'matriculas__ano_letivo')
            .order_by('nome_completo')
        )
        busca  = request.GET.get('q', '').strip()
        ativo  = request.GET.get('ativo', '')
        turma  = request.GET.get('turma', '')
        if busca:
            qs = qs.filter(
                Q(nome_completo__icontains=busca) | Q(matricula__icontains=busca)
            )
        if ativo == '1':
            qs = qs.filter(ativo=True)
        elif ativo == '0':
            qs = qs.filter(ativo=False)
        if turma:
            qs = qs.filter(matriculas__turma_id=turma, matriculas__ativo=True)

        from apps.turma.models import Turma
        turmas = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')

        return render(request, self.template_name, self._ctx(
            request, alunos=qs, turmas=turmas,
            filtros={'q': busca, 'ativo': ativo, 'turma': turma},
        ))


class CriarAlunoView(_EscritaMixin, View):
    template_name = 'aluno/form_aluno.html'

    def get(self, request):
        form = CriarAlunoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))

    def post(self, request):
        form = CriarAlunoForm(request.POST, request.FILES, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                responsavel_dados = None
                if cd.get('resp_nome'):
                    responsavel_dados = {
                        'nome':                  cd['resp_nome'],
                        'telefone':              cd.get('resp_telefone', ''),
                        'cpf':                   cd.get('resp_cpf', ''),
                        'parentesco':            cd['resp_parentesco'],
                        'responsavel_principal': cd.get('resp_principal', False),
                        'responsavel_financeiro': cd.get('resp_financeiro', False),
                    }
                aluno = aluno_service.criar(request.escola, {
                    'nome_completo':   cd['nome_completo'],
                    'data_nascimento': cd.get('data_nascimento'),
                    'cpf':             cd.get('cpf', ''),
                    'rg':              cd.get('rg', ''),
                    'foto':            cd.get('foto'),
                    'turma':           cd.get('turma'),
                    'ano_letivo':      cd.get('ano_letivo'),
                    'responsavel_dados': responsavel_dados,
                })
                messages.success(request, f'Aluno {cd["nome_completo"]} cadastrado com sucesso.')
                return redirect('aluno:detalhe', pk=aluno.pk)
            except Exception as exc:
                messages.error(request, f'Erro ao cadastrar: {exc}')
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))


class DetalheAlunoView(_LeituraMixin, View):
    template_name = 'aluno/detalhe.html'

    def get(self, request, pk):
        aluno = get_object_or_404(
            Aluno.objects.prefetch_related(
                'matriculas__turma', 'matriculas__ano_letivo',
            ),
            pk=pk, escola=request.escola,
        )
        mat_form           = MatriculaTurmaForm(escola=request.escola)
        troca_form         = TrocarTurmaForm(escola=request.escola)
        acesso_form        = AtivarAcessoForm()
        vincular_resp_form = VincularResponsavelForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(
            request, aluno=aluno, mat_form=mat_form, troca_form=troca_form,
            acesso_form=acesso_form, vincular_resp_form=vincular_resp_form,
        ))


class EditarAlunoView(_EscritaMixin, View):
    template_name = 'aluno/form_aluno.html'

    def _get_aluno(self, request, pk):
        return get_object_or_404(Aluno, pk=pk, escola=request.escola)

    def get(self, request, pk):
        aluno = self._get_aluno(request, pk)
        form  = EditarAlunoForm(instance=aluno)
        return render(request, self.template_name, self._ctx(request, form=form, editando=True, aluno=aluno))

    def post(self, request, pk):
        aluno = self._get_aluno(request, pk)
        form  = EditarAlunoForm(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            aluno_service.editar(aluno, form.cleaned_data)
            messages.success(request, 'Aluno atualizado com sucesso.')
            return redirect('aluno:detalhe', pk=aluno.pk)
        return render(request, self.template_name, self._ctx(request, form=form, editando=True, aluno=aluno))


class DesativarAlunoView(_EscritaMixin, View):
    def post(self, request, pk):
        aluno = get_object_or_404(Aluno, pk=pk, escola=request.escola)
        aluno_service.desativar(aluno)
        messages.success(request, f'{aluno.nome_completo} foi desativado.')
        return redirect('aluno:lista')


class ReativarAlunoView(_EscritaMixin, View):
    def post(self, request, pk):
        aluno = get_object_or_404(Aluno, pk=pk, escola=request.escola)
        aluno_service.reativar(aluno)
        messages.success(request, f'{aluno.nome_completo} foi reativado.')
        return redirect('aluno:lista')


class MatricularView(_EscritaMixin, View):
    def post(self, request, pk):
        aluno = get_object_or_404(Aluno, pk=pk, escola=request.escola)
        form  = MatriculaTurmaForm(request.POST, escola=request.escola)
        if form.is_valid():
            try:
                aluno_service.matricular(aluno, form.cleaned_data['turma'], form.cleaned_data['ano_letivo'])
                messages.success(request, 'Aluno matriculado com sucesso.')
            except ValueError as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, 'Dados de matrícula inválidos.')
        return redirect('aluno:detalhe', pk=aluno.pk)


class TrocarTurmaView(_EscritaMixin, View):
    def post(self, request, mat_pk):
        matricula = get_object_or_404(
            MatriculaTurma, pk=mat_pk, aluno__escola=request.escola, ativo=True,
        )
        form = TrocarTurmaForm(request.POST, escola=request.escola)
        if form.is_valid():
            aluno_service.trocar_turma(matricula, form.cleaned_data['nova_turma'])
            messages.success(request, 'Turma alterada com sucesso.')
        else:
            messages.error(request, 'Turma inválida.')
        return redirect('aluno:detalhe', pk=matricula.aluno_id)


class TransferirView(_EscritaMixin, View):
    def post(self, request, mat_pk):
        matricula = get_object_or_404(
            MatriculaTurma, pk=mat_pk, aluno__escola=request.escola, ativo=True,
        )
        aluno_service.transferir(matricula)
        messages.success(request, f'{matricula.aluno.nome_completo} transferido(a).')
        return redirect('aluno:lista')


class EvadiemView(_EscritaMixin, View):
    def post(self, request, mat_pk):
        matricula = get_object_or_404(
            MatriculaTurma, pk=mat_pk, aluno__escola=request.escola, ativo=True,
        )
        aluno_service.evadir(matricula)
        messages.success(request, f'{matricula.aluno.nome_completo} marcado(a) como evadido(a).')
        return redirect('aluno:lista')


class ConcluirView(_EscritaMixin, View):
    def post(self, request, mat_pk):
        matricula = get_object_or_404(
            MatriculaTurma, pk=mat_pk, aluno__escola=request.escola, ativo=True,
        )
        aluno_service.concluir(matricula)
        messages.success(request, f'{matricula.aluno.nome_completo} marcado(a) como concluinte.')
        return redirect('aluno:detalhe', pk=matricula.aluno_id)


class AtivarAcessoView(_EscritaMixin, View):
    def post(self, request, pk):
        aluno = get_object_or_404(Aluno, pk=pk, escola=request.escola)
        if aluno.usuario_id:
            messages.warning(request, f'{aluno.nome_completo} já possui acesso ao sistema.')
            return redirect('aluno:detalhe', pk=aluno.pk)
        form = AtivarAcessoForm(request.POST)
        if form.is_valid():
            try:
                aluno_service.ativar_acesso(aluno, form.cleaned_data['email'], form.cleaned_data['senha'])
                messages.success(request, f'Acesso ativado para {aluno.nome_completo}.')
            except ValueError as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, 'Dados inválidos.')
        return redirect('aluno:detalhe', pk=aluno.pk)


class VincularResponsavelAlunoView(_EscritaMixin, View):
    def post(self, request, pk):
        aluno = get_object_or_404(Aluno, pk=pk, escola=request.escola)
        form  = VincularResponsavelForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                from apps.responsavel.services import responsavel_service
                responsavel_service.vincular_aluno(
                    perfil=cd['responsavel'],
                    aluno=aluno,
                    dados={
                        'parentesco':             cd['parentesco'],
                        'responsavel_principal':  cd['responsavel_principal'],
                        'responsavel_financeiro': cd['responsavel_financeiro'],
                    },
                )
                messages.success(request, f'{cd["responsavel"].nome} vinculado(a) com sucesso.')
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        else:
            messages.error(request, 'Dados inválidos.')
        return redirect('aluno:detalhe', pk=aluno.pk)


# ---------------------------------------------------------------------------
# Portal do Aluno
# ---------------------------------------------------------------------------

class _AlunoMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo != 'ALUNO':
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class DashboardAlunoView(_AlunoMixin, View):
    template_name = 'aluno/portal_dashboard.html'

    def get(self, request):
        from apps.boletim.models import ResultadoPeriodo
        from apps.avaliacao.models import Avaliacao
        from apps.comunicado.models import Comunicado
        from apps.ano_letivo.models import PeriodoLetivo
        from django.db.models import Avg
        import datetime

        try:
            aluno = request.user.aluno
        except Exception:
            aluno = None

        matricula_ativa = ano_letivo = periodo_atual = None
        resultados_periodo = []
        avaliacoes_proximas = []
        freq_media = None

        if aluno:
            matricula_ativa = (
                aluno.matriculas
                .filter(ativo=True)
                .select_related('turma__serie', 'ano_letivo')
                .first()
            )
            if matricula_ativa:
                ano_letivo = matricula_ativa.ano_letivo
                periodo_atual = (
                    PeriodoLetivo.objects
                    .filter(ano_letivo=ano_letivo)
                    .order_by('-numero')
                    .first()
                )
                resultados_qs = (
                    ResultadoPeriodo.objects
                    .filter(aluno=aluno, ano_letivo=ano_letivo, periodo_letivo=periodo_atual)
                    .select_related('materia', 'periodo_letivo')
                    .order_by('materia__nome')
                ) if periodo_atual else ResultadoPeriodo.objects.none()

                freq_media = resultados_qs.aggregate(
                    Avg('frequencia_percentual')
                )['frequencia_percentual__avg']
                resultados_periodo = list(resultados_qs)

                avaliacoes_proximas = (
                    Avaliacao.objects
                    .filter(
                        turma=matricula_ativa.turma,
                        ano_letivo=ano_letivo,
                        publicada=True,
                        data_aplicacao__gte=datetime.date.today(),
                    )
                    .select_related('materia')
                    .order_by('data_aplicacao')[:5]
                )

        comunicados_recentes = (
            Comunicado.objects
            .filter(escola=request.escola, publicada=True)
            .order_by('-criado_em')[:5]
        )

        return render(request, self.template_name, self._ctx(
            request,
            active_nav='dashboard',
            aluno=aluno,
            matricula_ativa=matricula_ativa,
            ano_letivo=ano_letivo,
            periodo_atual=periodo_atual,
            freq_media=freq_media,
            resultados_periodo=resultados_periodo,
            avaliacoes_proximas=avaliacoes_proximas,
            comunicados_recentes=comunicados_recentes,
        ))


class PerfilAlunoView(_AlunoMixin, View):
    template_name = 'aluno/portal_perfil.html'

    def get(self, request):
        try:
            aluno = request.user.aluno
        except Exception:
            aluno = None

        matricula_ativa = (
            aluno.matriculas
            .filter(ativo=True)
            .select_related('turma__serie', 'ano_letivo')
            .first()
        ) if aluno else None

        return render(request, self.template_name, self._ctx(
            request,
            active_nav='perfil',
            aluno=aluno,
            matricula_ativa=matricula_ativa,
        ))
