from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import ResultadoAnual, ResultadoPeriodo
from .services import boletim_service


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
# Lista de turmas / seleção
# ---------------------------------------------------------------------------

class BoletimIndexView(_LeituraMixin, View):
    template_name = 'boletim/index.html'

    def get(self, request):
        from apps.turma.models import Turma
        from apps.ano_letivo.models import AnoLetivo

        anos = AnoLetivo.objects.filter(escola=request.escola).order_by('-ano')
        ano_id = request.GET.get('ano_letivo', '')
        turmas = []
        ano_selecionado = None
        if ano_id:
            try:
                ano_selecionado = anos.get(pk=ano_id)
                turmas = (
                    Turma.objects
                    .filter(escola=request.escola, ano_letivo=ano_selecionado)
                    .select_related('serie', 'ano_letivo')
                    .order_by('nome')
                )
            except AnoLetivo.DoesNotExist:
                pass

        return render(request, self.template_name, self._ctx(
            request, anos=anos, turmas=turmas,
            ano_selecionado=ano_selecionado, ano_id=ano_id,
        ))


# ---------------------------------------------------------------------------
# Lista de alunos de uma turma com resumo do boletim
# ---------------------------------------------------------------------------

class BoletimTurmaView(_LeituraMixin, View):
    template_name = 'boletim/turma.html'

    def get(self, request, turma_pk):
        from apps.turma.models import Turma
        from apps.aluno.models import MatriculaTurma

        turma = get_object_or_404(
            Turma.objects.select_related('ano_letivo', 'serie'),
            pk=turma_pk, escola=request.escola,
        )
        matriculas = (
            MatriculaTurma.objects
            .filter(turma=turma, ano_letivo=turma.ano_letivo, ativo=True)
            .select_related('aluno')
            .order_by('aluno__nome_completo')
        )
        # Build quick summary per aluno: count of REPROVADO/RECUPERACAO resultados
        from apps.ano_letivo.models import PeriodoLetivo
        periodos = PeriodoLetivo.objects.filter(ano_letivo=turma.ano_letivo).order_by('numero')

        alunos_resumo = []
        for mat in matriculas:
            resultados = ResultadoPeriodo.objects.filter(
                aluno=mat.aluno,
                ano_letivo=turma.ano_letivo,
            ).select_related('materia')
            alunos_resumo.append({
                'aluno': mat.aluno,
                'resultados': resultados,
            })

        return render(request, self.template_name, self._ctx(
            request,
            turma=turma,
            periodos=periodos,
            alunos_resumo=alunos_resumo,
        ))


# ---------------------------------------------------------------------------
# Boletim individual
# ---------------------------------------------------------------------------

class BoletimAlunoView(_LeituraMixin, View):
    template_name = 'boletim/boletim.html'

    def get(self, request, aluno_pk, ano_letivo_pk):
        from apps.aluno.models import Aluno, MatriculaTurma
        from apps.ano_letivo.models import AnoLetivo, PeriodoLetivo
        from apps.materia.models import Materia

        aluno = get_object_or_404(Aluno, pk=aluno_pk, escola=request.escola)
        ano_letivo = get_object_or_404(AnoLetivo, pk=ano_letivo_pk, escola=request.escola)

        periodos = PeriodoLetivo.objects.filter(ano_letivo=ano_letivo).order_by('numero')

        # Get all matérias that have at least one avaliação for this aluno's turma in this year
        matricula = (
            MatriculaTurma.objects
            .filter(aluno=aluno, ano_letivo=ano_letivo, ativo=True)
            .select_related('turma')
            .first()
        )

        from apps.avaliacao.models import Avaliacao
        if matricula:
            materia_ids = (
                Avaliacao.objects
                .filter(turma=matricula.turma, ano_letivo=ano_letivo)
                .values_list('materia_id', flat=True)
                .distinct()
            )
            materias = Materia.objects.filter(pk__in=materia_ids, ativo=True).order_by('nome')
        else:
            materias = Materia.objects.none()

        # Build grid: {materia: {periodo_pk: ResultadoPeriodo or None}}
        resultados_periodo = {
            r.materia_id: r
            for r in ResultadoPeriodo.objects.filter(aluno=aluno, ano_letivo=ano_letivo)
            .select_related('materia', 'periodo_letivo')
        }
        # By (materia_id, periodo_id)
        rp_map = {}
        for rp in ResultadoPeriodo.objects.filter(aluno=aluno, ano_letivo=ano_letivo):
            rp_map[(rp.materia_id, rp.periodo_letivo_id)] = rp

        resultados_anuais = {
            r.materia_id: r
            for r in ResultadoAnual.objects.filter(aluno=aluno, ano_letivo=ano_letivo)
        }

        linhas = []
        for materia in materias:
            cols = [rp_map.get((materia.pk, p.pk)) for p in periodos]
            anual = resultados_anuais.get(materia.pk)
            linhas.append({'materia': materia, 'periodos': cols, 'anual': anual})

        return render(request, self.template_name, self._ctx(
            request,
            aluno=aluno,
            ano_letivo=ano_letivo,
            periodos=periodos,
            linhas=linhas,
            matricula=matricula,
        ))


# ---------------------------------------------------------------------------
# Calcular período para toda a turma (POST)
# ---------------------------------------------------------------------------

class CalcularPeriodoTurmaView(_DiretorMixin, View):
    def post(self, request, turma_pk, periodo_pk):
        from apps.turma.models import Turma
        from apps.ano_letivo.models import PeriodoLetivo

        turma = get_object_or_404(Turma, pk=turma_pk, escola=request.escola)
        periodo = get_object_or_404(PeriodoLetivo, pk=periodo_pk)

        count = boletim_service.calcular_periodo_turma(turma, periodo)
        messages.success(request, f'Resultados do {periodo.nome} recalculados ({count} entradas).')
        return redirect('boletim:turma', turma_pk=turma_pk)


# ---------------------------------------------------------------------------
# Calcular resultados anuais para toda a turma (POST)
# ---------------------------------------------------------------------------

class CalcularAnoTurmaView(_DiretorMixin, View):
    def post(self, request, turma_pk):
        from apps.turma.models import Turma

        turma = get_object_or_404(Turma, pk=turma_pk, escola=request.escola)
        count = boletim_service.calcular_ano_turma(turma, turma.ano_letivo)
        messages.success(request, f'Resultados anuais calculados ({count} entradas).')
        return redirect('boletim:turma', turma_pk=turma_pk)


# ---------------------------------------------------------------------------
# Aprovar por conselho de classe (POST)
# ---------------------------------------------------------------------------

class AprovarConselhoView(_DiretorMixin, View):
    def post(self, request, resultado_pk):
        resultado = get_object_or_404(
            ResultadoAnual.objects.select_related('aluno__escola'),
            pk=resultado_pk,
            aluno__escola=request.escola,
        )
        boletim_service.aprovar_conselho(resultado, request=request)
        messages.success(request, f'Aprovação por conselho registrada para {resultado.aluno.nome_completo} — {resultado.materia.nome}.')
        return redirect('boletim:boletim_aluno', aluno_pk=resultado.aluno_id, ano_letivo_pk=resultado.ano_letivo_id)


# ---------------------------------------------------------------------------
# PDF do boletim
# ---------------------------------------------------------------------------

class BoletimPDFView(_LeituraMixin, View):
    def get(self, request, aluno_pk, ano_letivo_pk):
        from apps.aluno.models import Aluno, MatriculaTurma
        from apps.ano_letivo.models import AnoLetivo, PeriodoLetivo
        from apps.materia.models import Materia
        from apps.avaliacao.models import Avaliacao

        aluno = get_object_or_404(Aluno, pk=aluno_pk, escola=request.escola)
        ano_letivo = get_object_or_404(AnoLetivo, pk=ano_letivo_pk, escola=request.escola)

        periodos = PeriodoLetivo.objects.filter(ano_letivo=ano_letivo).order_by('numero')
        matricula = (
            MatriculaTurma.objects
            .filter(aluno=aluno, ano_letivo=ano_letivo, ativo=True)
            .select_related('turma')
            .first()
        )

        if matricula:
            materia_ids = (
                Avaliacao.objects
                .filter(turma=matricula.turma, ano_letivo=ano_letivo)
                .values_list('materia_id', flat=True)
                .distinct()
            )
            materias = Materia.objects.filter(pk__in=materia_ids, ativo=True).order_by('nome')
        else:
            materias = Materia.objects.none()

        rp_map = {
            (r.materia_id, r.periodo_letivo_id): r
            for r in ResultadoPeriodo.objects.filter(aluno=aluno, ano_letivo=ano_letivo)
        }
        resultados_anuais = {
            r.materia_id: r
            for r in ResultadoAnual.objects.filter(aluno=aluno, ano_letivo=ano_letivo)
        }

        linhas = []
        for materia in materias:
            cols = [rp_map.get((materia.pk, p.pk)) for p in periodos]
            anual = resultados_anuais.get(materia.pk)
            linhas.append({'materia': materia, 'periodos': cols, 'anual': anual})

        html_content = render(request, 'boletim/boletim_pdf.html', {
            'aluno': aluno,
            'escola': request.escola,
            'ano_letivo': ano_letivo,
            'periodos': periodos,
            'linhas': linhas,
            'matricula': matricula,
        }).content

        try:
            from weasyprint import HTML
            pdf = HTML(string=html_content.decode('utf-8')).write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="boletim_{aluno.matricula}_{ano_letivo.ano}.pdf"'
            return response
        except ImportError:
            messages.error(request, 'WeasyPrint não está instalado. Instale com: pip install weasyprint')
            return redirect('boletim:boletim_aluno', aluno_pk=aluno_pk, ano_letivo_pk=ano_letivo_pk)
