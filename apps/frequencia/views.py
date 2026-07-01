from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import RegistroFrequenciaForm
from .models import PresencaAluno, RegistroFrequencia
from .services import frequencia_service


class _LeituraMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in ('DIRETOR', 'FUNCIONARIO', 'PROFESSOR'):
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
# Lista de registros
# ---------------------------------------------------------------------------

class ListarRegistrosView(_LeituraMixin, View):
    template_name = 'frequencia/lista.html'

    def get(self, request):
        escola = request.escola
        qs = (
            RegistroFrequencia.objects
            .filter(turma__escola=escola)
            .select_related('turma', 'materia', 'professor__papel__vinculo__usuario',
                            'ano_letivo', 'periodo_letivo')
            .order_by('-data', '-criado_em')
        )
        turma_id  = request.GET.get('turma', '')
        data_str  = request.GET.get('data', '')
        if turma_id:
            qs = qs.filter(turma_id=turma_id)
        if data_str:
            qs = qs.filter(data=data_str)

        from apps.turma.models import Turma
        turmas = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
        return render(request, self.template_name, self._ctx(
            request,
            registros=qs[:100],
            turmas=turmas,
            filtros={'turma': turma_id, 'data': data_str},
        ))


# ---------------------------------------------------------------------------
# Criar registro
# ---------------------------------------------------------------------------

class CriarRegistroView(_LeituraMixin, View):
    template_name = 'frequencia/form_registro.html'

    def get(self, request):
        form = RegistroFrequenciaForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = RegistroFrequenciaForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            registro = frequencia_service.criar_registro(
                turma          = cd['turma'],
                materia        = cd.get('materia'),
                professor      = cd.get('professor'),
                data           = cd['data'],
                ano_letivo     = cd['ano_letivo'],
                periodo_letivo = cd.get('periodo_letivo'),
                criado_por     = request.user,
            )
            messages.success(request, 'Registro criado. Lance as presenças abaixo.')
            return redirect('frequencia:lancar', pk=registro.pk)
        return render(request, self.template_name, self._ctx(request, form=form))


# ---------------------------------------------------------------------------
# Detalhe do registro
# ---------------------------------------------------------------------------

class DetalheRegistroView(_LeituraMixin, View):
    template_name = 'frequencia/detalhe.html'

    def get(self, request, pk):
        registro = get_object_or_404(
            RegistroFrequencia.objects.select_related(
                'turma', 'materia', 'professor__papel__vinculo__usuario',
                'ano_letivo', 'periodo_letivo',
            ),
            pk=pk, turma__escola=request.escola,
        )
        presencas = (
            registro.presencas
            .select_related('aluno')
            .order_by('aluno__nome_completo')
        )
        return render(request, self.template_name, self._ctx(
            request, registro=registro, presencas=presencas,
        ))


# ---------------------------------------------------------------------------
# Lançar presenças
# ---------------------------------------------------------------------------

class LancarPresencasView(_LeituraMixin, View):
    template_name = 'frequencia/lancar.html'

    def _get_registro(self, request, pk):
        return get_object_or_404(
            RegistroFrequencia.objects.select_related(
                'turma__escola', 'materia', 'ano_letivo', 'periodo_letivo',
            ),
            pk=pk, turma__escola=request.escola,
        )

    def get(self, request, pk):
        registro = self._get_registro(request, pk)
        from apps.aluno.models import MatriculaTurma
        matriculas = (
            MatriculaTurma.objects
            .filter(turma=registro.turma, ano_letivo=registro.ano_letivo, ativo=True)
            .select_related('aluno')
            .order_by('aluno__nome_completo')
        )
        presencas_map = {p.aluno_id: p for p in registro.presencas.all()}
        alunos_list = [
            (mat.aluno, presencas_map.get(mat.aluno_id))
            for mat in matriculas
        ]
        return render(request, self.template_name, self._ctx(
            request, registro=registro, alunos_list=alunos_list,
        ))

    def post(self, request, pk):
        registro = self._get_registro(request, pk)
        from apps.aluno.models import MatriculaTurma
        matriculas = (
            MatriculaTurma.objects
            .filter(turma=registro.turma, ano_letivo=registro.ano_letivo, ativo=True)
            .select_related('aluno')
        )
        entradas = []
        for mat in matriculas:
            aid = mat.aluno_id
            presente    = bool(request.POST.get(f'presente_{aid}'))
            justificado = bool(request.POST.get(f'justificado_{aid}')) and not presente
            observacao  = request.POST.get(f'obs_{aid}', '').strip()
            entradas.append({
                'aluno_id':   aid,
                'presente':   presente,
                'justificado': justificado,
                'observacao': observacao,
            })
        count = frequencia_service.lancar_presencas(registro, entradas)
        messages.success(request, f'Presenças salvas ({count} alunos).')
        return redirect('frequencia:detalhe', pk=pk)


# ---------------------------------------------------------------------------
# Justificar falta (POST only)
# ---------------------------------------------------------------------------

class JustificarFaltaView(_LeituraMixin, View):
    def post(self, request, pk):
        presenca = get_object_or_404(
            PresencaAluno.objects.select_related('registro__turma__escola'),
            pk=pk, registro__turma__escola=request.escola,
        )
        obs = request.POST.get('observacao', '').strip()
        frequencia_service.justificar_falta(presenca, obs)
        messages.success(request, 'Falta justificada.')
        return redirect('frequencia:detalhe', pk=presenca.registro_id)


# ---------------------------------------------------------------------------
# Cancelar aula (POST only) — DIRETOR only
# ---------------------------------------------------------------------------

class CancelarAulaView(_DiretorMixin, View):
    def post(self, request, pk):
        registro = get_object_or_404(
            RegistroFrequencia, pk=pk, turma__escola=request.escola,
        )
        frequencia_service.cancelar_aula(registro)
        messages.success(request, 'Aula cancelada e registros removidos.')
        return redirect('frequencia:lista')


# ---------------------------------------------------------------------------
# Frequência de um aluno (visão geral por período)
# ---------------------------------------------------------------------------

class FrequenciaAlunoView(_LeituraMixin, View):
    template_name = 'frequencia/aluno.html'

    def get(self, request, aluno_pk, ano_letivo_pk):
        from apps.aluno.models import Aluno, MatriculaTurma
        from apps.ano_letivo.models import AnoLetivo, PeriodoLetivo
        from apps.materia.models import Materia

        aluno = get_object_or_404(Aluno, pk=aluno_pk, escola=request.escola)
        ano_letivo = get_object_or_404(AnoLetivo, pk=ano_letivo_pk, escola=request.escola)

        periodos = PeriodoLetivo.objects.filter(ano_letivo=ano_letivo).order_by('numero')
        matricula = (
            MatriculaTurma.objects
            .filter(aluno=aluno, ano_letivo=ano_letivo, ativo=True)
            .select_related('turma')
            .first()
        )

        # Materias with any registro in this turma/year
        if matricula:
            materia_ids = (
                RegistroFrequencia.objects
                .filter(turma=matricula.turma, ano_letivo=ano_letivo)
                .values_list('materia_id', flat=True)
                .distinct()
            )
            materias = Materia.objects.filter(pk__in=materia_ids, ativo=True).order_by('nome')
        else:
            materias = Materia.objects.none()

        # Build grid: materia × periodo → (percentual, total_aulas, presentes)
        linhas = []
        for materia in materias:
            cols = []
            for periodo in periodos:
                pct = frequencia_service.calcular_percentual(aluno, materia, periodo)
                total = RegistroFrequencia.objects.filter(
                    turma=matricula.turma if matricula else None,
                    materia=materia,
                    periodo_letivo=periodo,
                ).count() if matricula else 0
                presentes = PresencaAluno.objects.filter(
                    registro__turma=matricula.turma if matricula else None,
                    registro__materia=materia,
                    registro__periodo_letivo=periodo,
                    aluno=aluno,
                    presente=True,
                ).count() if matricula else 0
                cols.append({'pct': pct, 'total': total, 'presentes': presentes})
            linhas.append({'materia': materia, 'cols': cols})

        # Presencas detail (last 30 records)
        presencas_recentes = (
            PresencaAluno.objects
            .filter(aluno=aluno, registro__ano_letivo=ano_letivo)
            .select_related('registro__materia', 'registro__turma')
            .order_by('-registro__data')[:30]
        )

        return render(request, self.template_name, self._ctx(
            request,
            aluno=aluno,
            ano_letivo=ano_letivo,
            periodos=periodos,
            linhas=linhas,
            matricula=matricula,
            presencas_recentes=presencas_recentes,
        ))
