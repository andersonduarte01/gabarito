from calendar import monthrange
from datetime import date, timedelta

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import PresencaAluno, RegistroFrequencia
from .services import frequencia_service


_DIAS_PT = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex'}

_MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}


def _turma_ids_professor(papel):
    try:
        from apps.turma.models import ProfessorMateriaTurma
        return list(
            ProfessorMateriaTurma.objects
            .filter(professor=papel.perfil_professor, ativo=True)
            .values_list('turma_id', flat=True)
        )
    except Exception:
        return []


def _semana_de(d):
    return d - timedelta(days=d.weekday())


def _mes_de(d):
    return d.replace(day=1)


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
# Lista — Gerenciador de cadernetas (colaborador)
# ---------------------------------------------------------------------------

class ListarRegistrosView(_LeituraMixin, View):
    template_name = 'frequencia/lista.html'

    def get(self, request):
        from apps.turma.models import Turma, ProfessorMateriaTurma
        from apps.ano_letivo.models import AnoLetivo, PeriodoLetivo, StatusAnoLetivo, TipoPeriodo
        from django.db.models import Count

        escola = request.escola
        hoje = date.today()

        try:
            week_start = _semana_de(date.fromisoformat(request.GET.get('semana', '')))
        except (ValueError, TypeError):
            week_start = _semana_de(hoje)

        dias = [week_start + timedelta(days=i) for i in range(5)]
        week_end = dias[-1]
        prev_week = week_start - timedelta(weeks=1)
        next_week = week_start + timedelta(weeks=1)
        pode_avancar = week_start < _semana_de(hoje + timedelta(weeks=1))

        turmas_qs = (
            Turma.objects
            .filter(escola=escola, ativo=True)
            .select_related('serie')
            .order_by('nome')
        )
        if request.papel.tipo == 'PROFESSOR':
            turmas_qs = turmas_qs.filter(pk__in=_turma_ids_professor(request.papel))

        turmas = list(turmas_qs)

        registros_set = set(
            RegistroFrequencia.objects
            .filter(turma__in=turmas, data__in=dias)
            .values_list('turma_id', 'data')
        )

        anos_qs = AnoLetivo.objects.filter(escola=escola).order_by('-ano')
        ano_ativo = (
            anos_qs.filter(status=StatusAnoLetivo.EM_ANDAMENTO).first()
            or anos_qs.first()
        )
        ano_id = ano_ativo.pk if ano_ativo else ''

        periodos_vigentes = (
            list(PeriodoLetivo.objects.filter(ano_letivo=ano_ativo))
            if ano_ativo else []
        )

        def _tipo_dia(d):
            for p in periodos_vigentes:
                if p.data_inicio <= d <= p.data_fim:
                    return p.tipo
            return None

        materia_map = {}
        for r in (
            RegistroFrequencia.objects
            .filter(turma__in=turmas)
            .values('turma_id', 'materia_id')
            .annotate(n=Count('id'))
            .order_by('turma_id', '-n')
        ):
            if r['turma_id'] not in materia_map:
                materia_map[r['turma_id']] = r['materia_id']

        prof_map = {}
        for pmt in (
            ProfessorMateriaTurma.objects
            .filter(turma__in=turmas, ativo=True)
            .select_related('professor__papel__vinculo__usuario', 'materia')
        ):
            tid = pmt.turma_id
            if tid not in prof_map:
                try:
                    prof_map[tid] = pmt.professor.papel.vinculo.usuario.nome
                except Exception:
                    pass
            if tid not in materia_map and pmt.materia_id:
                materia_map[tid] = pmt.materia_id

        linhas = []
        for turma in turmas:
            cells = []
            pendente = False
            for dia in dias:
                lancado = (turma.pk, dia) in registros_set
                futuro  = dia > hoje
                tipo    = _tipo_dia(dia)
                recesso = tipo == TipoPeriodo.RECESSO
                if not lancado and not futuro and not recesso and tipo == TipoPeriodo.LETIVO:
                    pendente = True
                cells.append({
                    'dia':     dia,
                    'nome':    _DIAS_PT[dia.weekday()],
                    'lancado': lancado,
                    'futuro':  futuro,
                    'recesso': recesso,
                })
            linhas.append({
                'turma':            turma,
                'cells':            cells,
                'pendente':         pendente,
                'professor':        prof_map.get(turma.pk, '—'),
                'pendencias_count': sum(1 for c in cells if not c['lancado'] and not c['futuro'] and not c['recesso']),
                'materia_id':       materia_map.get(turma.pk, ''),
                'ano_id':           ano_id,
            })

        linhas.sort(key=lambda x: (not x['pendente'], x['turma'].nome))

        pendentes_count = sum(1 for l in linhas if l['pendente'])

        return render(request, self.template_name, self._ctx(
            request,
            dias=dias,
            week_start=week_start,
            week_end=week_end,
            prev_week=prev_week,
            next_week=next_week,
            pode_avancar=pode_avancar,
            hoje=hoje,
            linhas=linhas,
            pendentes_count=pendentes_count,
        ))


# ---------------------------------------------------------------------------
# Caderneta Digital — visão semanal
# ---------------------------------------------------------------------------

class CadernetaView(_LeituraMixin, View):
    template_name = 'frequencia/caderneta.html'

    def get(self, request):
        from apps.turma.models import Turma
        from apps.materia.models import Materia
        from apps.aluno.models import MatriculaTurma
        from apps.ano_letivo.models import AnoLetivo, PeriodoLetivo, StatusAnoLetivo, TipoPeriodo

        escola = request.escola
        hoje = date.today()

        if request.papel.tipo == 'PROFESSOR':
            turmas_qs = Turma.objects.filter(
                pk__in=_turma_ids_professor(request.papel), ativo=True
            ).order_by('nome')
        else:
            turmas_qs = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')

        materias_qs = Materia.objects.filter(escola=escola, ativo=True).order_by('nome')
        anos_qs = AnoLetivo.objects.filter(escola=escola).order_by('-ano')

        # Apenas períodos letivos (sem recesso) para os filtros
        todos_periodos = (
            PeriodoLetivo.objects
            .filter(ano_letivo__escola=escola, tipo=TipoPeriodo.LETIVO)
            .select_related('ano_letivo')
            .order_by('ano_letivo__ano', 'numero')
        )

        turma_id   = request.GET.get('turma', '')
        materia_id = request.GET.get('materia', '')
        ano_id     = request.GET.get('ano_letivo', '')
        periodo_id = request.GET.get('periodo_letivo', '')

        if not ano_id:
            ano_ref = (
                anos_qs.filter(status=StatusAnoLetivo.EM_ANDAMENTO).first()
                or anos_qs.first()
            )
            if ano_ref:
                ano_id = str(ano_ref.pk)

        turma = materia = ano_letivo = periodo = None
        linhas = []
        col_stats = []
        dias = []
        mes_start = _mes_de(hoje)
        prev_mes = next_mes = None
        pode_prev = pode_next = False
        mes_nome = ''
        filtrado = bool(turma_id and materia_id and ano_id)

        if filtrado:
            try:
                turma      = get_object_or_404(Turma,     pk=turma_id,   escola=escola)
                materia    = get_object_or_404(Materia,   pk=materia_id, escola=escola)
                ano_letivo = get_object_or_404(AnoLetivo, pk=ano_id,     escola=escola)

                periodos_do_ano = PeriodoLetivo.objects.filter(
                    ano_letivo=ano_letivo, tipo=TipoPeriodo.LETIVO
                ).order_by('numero')

                if not periodo_id:
                    # Auto-seleção inteligente: nunca pega recesso; no gap usa o mais recente encerrado
                    p_auto = (
                        periodos_do_ano.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first()
                        or periodos_do_ano.filter(data_fim__lt=hoje).order_by('-data_fim').first()
                        or periodos_do_ano.order_by('data_inicio').first()
                    )
                    if p_auto:
                        periodo_id = str(p_auto.pk)

                periodo = periodos_do_ano.filter(pk=periodo_id).first() if periodo_id else None

                ref = periodo or ano_letivo
                p_inicio = ref.data_inicio
                p_fim    = ref.data_fim

                min_mes = _mes_de(p_inicio)
                max_mes = _mes_de(p_fim)

                try:
                    mes_raw = request.GET.get('mes', '')
                    y, m = mes_raw.split('-')
                    mes_start = date(int(y), int(m), 1)
                except Exception:
                    # No gap entre períodos: abre no último mês do período selecionado
                    ref_date = max(p_inicio, min(p_fim, hoje))
                    mes_start = _mes_de(ref_date)

                mes_start = max(min_mes, min(max_mes, mes_start))

                _, last_day = monthrange(mes_start.year, mes_start.month)
                mes_end = mes_start.replace(day=last_day)

                prev_mes = _mes_de(mes_start - timedelta(days=1))
                next_mes = _mes_de(mes_end + timedelta(days=1))
                pode_prev = prev_mes >= min_mes
                pode_next = next_mes <= max_mes
                mes_nome  = f"{_MESES_PT[mes_start.month]} {mes_start.year}"

                dias = [
                    mes_start + timedelta(days=i)
                    for i in range((mes_end - mes_start).days + 1)
                    if (mes_start + timedelta(days=i)).weekday() < 5
                    and p_inicio <= mes_start + timedelta(days=i) <= p_fim
                ]

                reg_qs = (
                    RegistroFrequencia.objects
                    .filter(turma=turma, materia=materia, ano_letivo=ano_letivo, data__in=dias)
                    .prefetch_related('presencas')
                )
                registros_por_data = {r.data: r for r in reg_qs}

                matriculas = (
                    MatriculaTurma.objects
                    .filter(turma=turma, ano_letivo=ano_letivo, ativo=True)
                    .select_related('aluno')
                    .order_by('aluno__nome_completo')
                )
                alunos = [m.aluno for m in matriculas]

                presencas_map = {a.pk: {} for a in alunos}
                for data_d, reg in registros_por_data.items():
                    for p in reg.presencas.all():
                        if p.aluno_id in presencas_map:
                            presencas_map[p.aluno_id][data_d] = p

                total_por_aluno = {}
                presentes_por_aluno = {}
                for aluno in alunos:
                    tots = presents = 0
                    for data_d, reg in registros_por_data.items():
                        if data_d > hoje:
                            continue
                        tots += 1
                        p = presencas_map[aluno.pk].get(data_d)
                        if p is None or p.presente:
                            presents += 1
                    total_por_aluno[aluno.pk]    = tots
                    presentes_por_aluno[aluno.pk] = presents

                linhas = []
                for aluno in alunos:
                    cells = []
                    for dia in dias:
                        futuro = dia > hoje
                        if dia in registros_por_data and not futuro:
                            reg = registros_por_data[dia]
                            p   = presencas_map[aluno.pk].get(dia)
                            if p is None:
                                status = None        # sem PresencaAluno → não lançado para este aluno
                            elif p.presente:
                                status = 'P'
                            elif p.justificado:
                                status = 'J'
                            else:
                                status = 'F'
                            presenca_pk  = p.pk if p else None
                            registro_pk  = reg.pk
                        else:
                            status = None
                            presenca_pk  = None
                            registro_pk  = registros_por_data[dia].pk if dia in registros_por_data else None
                        cells.append({
                            'status':      status,
                            'data':        dia,
                            'presenca_pk': presenca_pk,
                            'registro_pk': registro_pk,
                            'futuro':      futuro,
                        })

                    tots = total_por_aluno[aluno.pk]
                    pres = presentes_por_aluno[aluno.pk]
                    pct  = round(pres / tots * 100) if tots else None
                    linhas.append({
                        'aluno':    aluno,
                        'cells':    cells,
                        'presentes': pres,
                        'total':    tots,
                        'pct':      pct,
                    })

                col_stats = [
                    {
                        'data':        dia,
                        'dia_semana':  _DIAS_PT[dia.weekday()],
                        'lancado':     dia in registros_por_data,
                        'registro_pk': registros_por_data[dia].pk if dia in registros_por_data else None,
                        'futuro':      dia > hoje,
                    }
                    for dia in dias
                ]

            except Exception as exc:
                messages.error(request, f'Erro ao carregar caderneta: {exc}')
                filtrado = False

        filtros = {
            'turma':        turma_id,
            'materia':      materia_id,
            'ano_letivo':   ano_id,
            'periodo_letivo': periodo_id,
        }

        return render(request, self.template_name, self._ctx(
            request,
            turmas_qs=turmas_qs,
            materias_qs=materias_qs,
            anos_qs=anos_qs,
            todos_periodos=todos_periodos,
            turma=turma,
            materia=materia,
            ano_letivo=ano_letivo,
            periodo=periodo,
            dias=dias,
            linhas=linhas,
            col_stats=col_stats,
            filtros=filtros,
            filtrado=filtrado,
            mes_start=mes_start,
            prev_mes=prev_mes,
            next_mes=next_mes,
            mes_nome=mes_nome,
            pode_prev=pode_prev,
            pode_next=pode_next,
            hoje=hoje,
        ))


# ---------------------------------------------------------------------------
# Iniciar aula — get_or_create registro → redireciona para lancar
# ---------------------------------------------------------------------------

class IniciarAulaView(_LeituraMixin, View):
    def get(self, request):
        from apps.turma.models import Turma
        from apps.materia.models import Materia
        from apps.ano_letivo.models import AnoLetivo, PeriodoLetivo, TipoPeriodo

        turma_id   = request.GET.get('turma')
        materia_id = request.GET.get('materia')
        data_str   = request.GET.get('data')
        ano_id     = request.GET.get('ano_letivo')
        back       = request.GET.get('back', '')

        try:
            turma   = get_object_or_404(Turma,     pk=turma_id,   escola=request.escola)
            materia = get_object_or_404(Materia,   pk=materia_id, escola=request.escola)
            ano     = get_object_or_404(AnoLetivo, pk=ano_id,     escola=request.escola)
            data_obj = date.fromisoformat(data_str)

            # Infere o período pela data — rejeita recesso e dias fora do calendário
            periodo = PeriodoLetivo.objects.filter(
                ano_letivo=ano,
                tipo=TipoPeriodo.LETIVO,
                data_inicio__lte=data_obj,
                data_fim__gte=data_obj,
            ).first()
            if not periodo:
                messages.error(request, 'A data selecionada está em período de recesso ou fora do calendário letivo.')
                return redirect(back or 'frequencia:caderneta')

            professor = None
            if request.papel.tipo == 'PROFESSOR':
                try:
                    professor = request.papel.perfil_professor
                except Exception:
                    pass

            registro, _ = RegistroFrequencia.objects.get_or_create(
                turma=turma, materia=materia, data=data_obj, ano_letivo=ano,
                defaults={
                    'professor':      professor,
                    'periodo_letivo': periodo,
                    'criado_por':     request.user,
                },
            )

            from urllib.parse import urlencode
            qs  = urlencode({'back': back}) if back else ''
            url = f'/frequencia/{registro.pk}/lancar/?' + qs if qs else f'/frequencia/{registro.pk}/lancar/'
            return redirect(url)

        except Exception as exc:
            messages.error(request, f'Erro ao iniciar aula: {exc}')
            return redirect('frequencia:caderneta')


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
        presencas = list(
            registro.presencas
            .select_related('aluno')
            .order_by('aluno__nome_completo')
        )
        presentes_count = sum(1 for p in presencas if p.presente)
        faltas_count    = len(presencas) - presentes_count
        return render(request, self.template_name, self._ctx(
            request,
            registro=registro,
            presencas=presencas,
            presentes_count=presentes_count,
            faltas_count=faltas_count,
        ))


# ---------------------------------------------------------------------------
# Lançar presenças — todos os alunos de um registro
# ---------------------------------------------------------------------------

class LancarPresencasView(_LeituraMixin, View):
    template_name = 'frequencia/lancar.html'

    def _get_registro(self, request, pk):
        qs = RegistroFrequencia.objects.select_related(
            'turma__escola', 'materia', 'ano_letivo', 'periodo_letivo',
        ).filter(turma__escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        return get_object_or_404(qs, pk=pk)

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
        alunos_list   = [(mat.aluno, presencas_map.get(mat.aluno_id)) for mat in matriculas]
        back          = request.GET.get('back', '')
        return render(request, self.template_name, self._ctx(
            request, registro=registro, alunos_list=alunos_list, back=back,
        ))

    def post(self, request, pk):
        registro = self._get_registro(request, pk)
        back     = request.POST.get('back', '')
        from apps.aluno.models import MatriculaTurma
        matriculas = (
            MatriculaTurma.objects
            .filter(turma=registro.turma, ano_letivo=registro.ano_letivo, ativo=True)
            .select_related('aluno')
        )
        entradas = []
        for mat in matriculas:
            aid = mat.aluno_id
            entradas.append({
                'aluno_id':    aid,
                'presente':    bool(request.POST.get(f'presente_{aid}')),
                'justificado': bool(request.POST.get(f'justificado_{aid}')) and not bool(request.POST.get(f'presente_{aid}')),
                'observacao':  request.POST.get(f'obs_{aid}', '').strip(),
            })
        count = frequencia_service.lancar_presencas(registro, entradas)
        messages.success(request, f'Frequência salva — {count} aluno{"s" if count != 1 else ""} registrado{"s" if count != 1 else ""}.')
        if back:
            return redirect(back)
        return redirect('frequencia:detalhe', pk=pk)


# ---------------------------------------------------------------------------
# Salvar presença individual — endpoint AJAX
# ---------------------------------------------------------------------------

class SalvarPresencaAjaxView(_LeituraMixin, View):
    def post(self, request):
        import json
        try:
            payload    = json.loads(request.body)
            turma_id   = payload.get('turma_id')
            materia_id = payload.get('materia_id')
            data_str   = payload.get('data')
            ano_id     = payload.get('ano_letivo_id')
            aluno_id   = payload.get('aluno_id')
            presente   = bool(payload.get('presente', True))
            justificado = bool(payload.get('justificado', False)) and not presente
            observacao  = payload.get('observacao', '').strip()

            from apps.turma.models import Turma
            from apps.materia.models import Materia
            from apps.ano_letivo.models import AnoLetivo, PeriodoLetivo, TipoPeriodo
            from apps.aluno.models import Aluno

            turma    = get_object_or_404(Turma,     pk=turma_id,   escola=request.escola)
            materia  = get_object_or_404(Materia,   pk=materia_id, escola=request.escola)
            ano      = get_object_or_404(AnoLetivo, pk=ano_id,     escola=request.escola)
            aluno    = get_object_or_404(Aluno,     pk=aluno_id,   escola=request.escola)
            data_obj = date.fromisoformat(data_str)

            # Infere período pela data — rejeita recesso
            periodo = PeriodoLetivo.objects.filter(
                ano_letivo=ano,
                tipo=TipoPeriodo.LETIVO,
                data_inicio__lte=data_obj,
                data_fim__gte=data_obj,
            ).first()
            if not periodo:
                return JsonResponse(
                    {'ok': False, 'msg': 'Data em período de recesso ou fora do calendário letivo.'},
                    status=400,
                )

            professor = None
            if request.papel.tipo == 'PROFESSOR':
                try:
                    professor = request.papel.perfil_professor
                except Exception:
                    pass

            registro, _ = RegistroFrequencia.objects.get_or_create(
                turma=turma, materia=materia, data=data_obj, ano_letivo=ano,
                defaults={
                    'professor':      professor,
                    'periodo_letivo': periodo,
                    'criado_por':     request.user,
                },
            )

            frequencia_service.lancar_presencas(registro, [{
                'aluno_id':    aluno.pk,
                'presente':    presente,
                'justificado': justificado,
                'observacao':  observacao,
            }])

            if presente:
                novo_status = 'P'
                label = 'Presente'
            elif justificado:
                novo_status = 'J'
                label = 'Justificado'
            else:
                novo_status = 'F'
                label = 'Falta'

            return JsonResponse({
                'ok':     True,
                'msg':    f'Presença salva — {label}.',
                'status': novo_status,
            })

        except Exception as exc:
            return JsonResponse({'ok': False, 'msg': str(exc)}, status=400)


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
        messages.success(request, 'Falta justificada com sucesso.')
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

        aluno      = get_object_or_404(Aluno,      pk=aluno_pk,      escola=request.escola)
        ano_letivo = get_object_or_404(AnoLetivo,  pk=ano_letivo_pk, escola=request.escola)

        periodos = PeriodoLetivo.objects.filter(ano_letivo=ano_letivo).order_by('numero')
        matricula = (
            MatriculaTurma.objects
            .filter(aluno=aluno, ano_letivo=ano_letivo, ativo=True)
            .select_related('turma')
            .first()
        )

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

        linhas = []
        for materia in materias:
            cols = []
            for periodo in periodos:
                pct = frequencia_service.calcular_percentual(aluno, materia, periodo)
                total = RegistroFrequencia.objects.filter(
                    turma=matricula.turma, materia=materia, periodo_letivo=periodo,
                ).count() if matricula else 0
                presentes = PresencaAluno.objects.filter(
                    registro__turma=matricula.turma, registro__materia=materia,
                    registro__periodo_letivo=periodo, aluno=aluno, presente=True,
                ).count() if matricula else 0
                cols.append({'pct': pct, 'total': total, 'presentes': presentes})
            linhas.append({'materia': materia, 'cols': cols})

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
