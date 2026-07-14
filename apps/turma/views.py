from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from django.urls import reverse

from apps.turma.models import DiaSemana, HorarioAula, PeriodoAula, Turma, Turno
from apps.turma.forms import PeriodoAulaForm, TurmaForm
from apps.turma.services import turma_service

_TURNOS_VALIDOS = {t.value for t in Turno}

_DIAS_SEMANA = [
    (DiaSemana.SEGUNDA, 'Seg'),
    (DiaSemana.TERCA,   'Ter'),
    (DiaSemana.QUARTA,  'Qua'),
    (DiaSemana.QUINTA,  'Qui'),
    (DiaSemana.SEXTA,   'Sex'),
]


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


class ListarTurmasView(_LeituraMixin, View):
    template_name = 'turma/lista.html'

    def get(self, request):
        escola = request.escola
        turmas = (
            Turma.objects
            .filter(escola=escola)
            .select_related('ano_letivo', 'serie', 'serie__segmento')
            .order_by('-ano_letivo__ano', 'serie__segmento__tipo', 'serie__ordem', 'nome', 'turno')
        )

        # Agrupa por ano letivo
        anos = {}
        for t in turmas:
            ano = t.ano_letivo
            if ano.pk not in anos:
                anos[ano.pk] = {'ano_letivo': ano, 'turmas': []}
            anos[ano.pk]['turmas'].append(t)

        return render(request, self.template_name, self._ctx(
            request,
            grupos=list(anos.values()),
        ))


class CriarTurmaView(_DiretorMixin, View):
    template_name = 'turma/form_turma.html'

    def get(self, request):
        form = TurmaForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=False,
        ))

    def post(self, request):
        form = TurmaForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            turma_service.criar(
                escola=request.escola,
                ano_letivo=cd['ano_letivo'],
                serie=cd['serie'],
                dados={
                    'nome':       cd['nome'],
                    'turno':      cd['turno'],
                    'capacidade': cd.get('capacidade'),
                },
            )
            messages.success(request, 'Turma criada com sucesso.')
            return redirect('turma:lista')
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=False,
        ))


class DetalheTurmaView(_LeituraMixin, View):
    template_name = 'turma/detalhe.html'

    def get(self, request, pk):
        turma = get_object_or_404(
            Turma.objects.select_related('ano_letivo', 'serie', 'serie__segmento'),
            pk=pk, escola=request.escola,
        )
        from apps.aluno.models import MatriculaTurma
        matriculas = (
            MatriculaTurma.objects
            .filter(turma=turma, ativo=True)
            .select_related('aluno')
            .order_by('aluno__nome_completo')
        )
        return render(request, self.template_name, self._ctx(
            request, turma=turma, matriculas=matriculas,
        ))


class EditarTurmaView(_DiretorMixin, View):
    template_name = 'turma/form_turma.html'

    def _get_turma(self, request, pk):
        return get_object_or_404(Turma, pk=pk, escola=request.escola)

    def get(self, request, pk):
        turma = self._get_turma(request, pk)
        form  = TurmaForm(escola=request.escola, initial={
            'ano_letivo': turma.ano_letivo_id,
            'serie':      turma.serie_id,
            'nome':       turma.nome,
            'turno':      turma.turno,
            'capacidade': turma.capacidade,
        })
        form.instance = turma
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, turma=turma,
        ))

    def post(self, request, pk):
        turma = self._get_turma(request, pk)
        form  = TurmaForm(request.POST, escola=request.escola)
        form.instance = turma
        if form.is_valid():
            cd = form.cleaned_data
            turma_service.editar(turma, {
                'ano_letivo': cd['ano_letivo'],
                'serie':      cd['serie'],
                'nome':       cd['nome'],
                'turno':      cd['turno'],
                'capacidade': cd.get('capacidade'),
            })
            messages.success(request, 'Turma atualizada.')
            return redirect('turma:detalhe', pk=turma.pk)
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, turma=turma,
        ))


class DesativarTurmaView(_DiretorMixin, View):
    def post(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk, escola=request.escola)
        turma_service.desativar(turma)
        messages.success(request, 'Turma desativada.')
        return redirect('turma:lista')


class ReativarTurmaView(_DiretorMixin, View):
    def post(self, request, pk):
        turma = get_object_or_404(Turma, pk=pk, escola=request.escola)
        turma_service.reativar(turma)
        messages.success(request, 'Turma reativada.')
        return redirect('turma:lista')


# ── Períodos de Aula ──────────────────────────────────────────────────────────

class PeriodosAulaView(_DiretorMixin, View):
    template_name = 'turma/periodos.html'

    def _turno_ativo(self, source):
        t = source.get('turno', Turno.MATUTINO)
        return t if t in _TURNOS_VALIDOS else Turno.MATUTINO

    def _ctx_periodos(self, request, turno, form, edit_form=None, edit_obj=None):
        periodos = (
            PeriodoAula.objects
            .filter(escola=request.escola, turno=turno)
            .order_by('numero')
        )
        turno_label = dict(Turno.choices).get(turno, turno)
        return self._ctx(
            request,
            periodos=periodos,
            turnos=Turno.choices,
            turno_ativo=turno,
            turno_label=turno_label,
            form=form,
            edit_form=edit_form,
            edit_obj=edit_obj,
        )

    def _redirect_turno(self, turno):
        return redirect(reverse('turma:periodos') + f'?turno={turno}')

    def get(self, request, periodo_pk=None):
        turno = self._turno_ativo(request.GET)
        edit_form = None
        edit_obj = None
        if periodo_pk:
            edit_obj = get_object_or_404(PeriodoAula, pk=periodo_pk, escola=request.escola)
            turno = edit_obj.turno
            edit_form = PeriodoAulaForm(initial={
                'numero': edit_obj.numero,
                'nome': edit_obj.nome,
                'hora_inicio': edit_obj.hora_inicio,
                'hora_fim': edit_obj.hora_fim,
            })
        return render(request, self.template_name,
                      self._ctx_periodos(request, turno, PeriodoAulaForm(), edit_form, edit_obj))

    def post(self, request, periodo_pk=None):
        turno = self._turno_ativo(request.POST)
        if periodo_pk:
            obj = get_object_or_404(PeriodoAula, pk=periodo_pk, escola=request.escola)
            turno = obj.turno
            form = PeriodoAulaForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                obj.numero = cd['numero']
                obj.nome = cd['nome']
                obj.hora_inicio = cd['hora_inicio']
                obj.hora_fim = cd['hora_fim']
                try:
                    obj.save()
                    messages.success(request, f'Período "{obj.nome}" atualizado.')
                    return self._redirect_turno(turno)
                except IntegrityError:
                    messages.error(request, 'Já existe um período com esse número neste turno.')
            return render(request, self.template_name,
                          self._ctx_periodos(request, turno, PeriodoAulaForm(), form, obj))
        else:
            form = PeriodoAulaForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                try:
                    PeriodoAula.objects.create(
                        escola=request.escola,
                        turno=turno,
                        numero=cd['numero'],
                        nome=cd['nome'],
                        hora_inicio=cd['hora_inicio'],
                        hora_fim=cd['hora_fim'],
                    )
                    messages.success(request, f'Período "{cd["nome"]}" criado.')
                    return self._redirect_turno(turno)
                except IntegrityError:
                    messages.error(request, 'Já existe um período com esse número neste turno.')
            return render(request, self.template_name,
                          self._ctx_periodos(request, turno, form))


class ExcluirPeriodoAulaView(_DiretorMixin, View):
    def post(self, request, periodo_pk):
        obj = get_object_or_404(PeriodoAula, pk=periodo_pk, escola=request.escola)
        nome = obj.nome
        turno = obj.turno
        try:
            obj.delete()
            messages.success(request, f'Período "{nome}" removido.')
        except Exception:
            messages.error(request, 'Não é possível remover um período que já possui horários cadastrados.')
        return redirect(reverse('turma:periodos') + f'?turno={turno}')


# ── Grade Horária ─────────────────────────────────────────────────────────────

class HorarioTurmaView(_LeituraMixin, View):
    template_name = 'turma/horario.html'

    def get(self, request, pk):
        import json
        from apps.materia.models import Materia
        from apps.professor.models import PerfilProfessor
        from apps.turma.models import ProfessorMateriaTurma

        turma = get_object_or_404(
            Turma.objects.select_related('ano_letivo', 'serie'),
            pk=pk, escola=request.escola,
        )
        periodos = (
            PeriodoAula.objects
            .filter(escola=request.escola, turno=turma.turno, ativo=True)
            .order_by('numero')
        )
        horarios = (
            HorarioAula.objects
            .filter(turma=turma, ano_letivo=turma.ano_letivo)
            .select_related('periodo', 'materia', 'professor__papel__vinculo__usuario')
        )
        horario_map = {(h.periodo_id, h.dia_semana): h for h in horarios}

        grade = []
        for periodo in periodos:
            cells = []
            for dia_val, dia_abrev in _DIAS_SEMANA:
                h = horario_map.get((periodo.pk, dia_val))
                cells.append({'dia': dia_val, 'dia_abrev': dia_abrev, 'horario': h})
            grade.append({'periodo': periodo, 'cells': cells})

        # Todas as matérias da escola (sem filtro)
        materias = list(Materia.objects.filter(escola=request.escola, ativo=True).order_by('nome'))

        # Todos os professores ativos da escola (fallback)
        todos_professores = [
            {'pk': p.pk, 'nome': p.papel.vinculo.usuario.nome}
            for p in (
                PerfilProfessor.objects
                .filter(papel__vinculo__escola=request.escola, papel__ativo=True)
                .select_related('papel__vinculo__usuario')
                .order_by('papel__vinculo__usuario__nome')
            )
        ]

        # Mapa materia_id → professores vinculados a essa matéria NESSA turma
        mp = {}
        for vmt in (
            ProfessorMateriaTurma.objects
            .filter(turma=turma, ano_letivo=turma.ano_letivo, ativo=True)
            .select_related('professor__papel__vinculo__usuario')
            .order_by('professor__papel__vinculo__usuario__nome')
        ):
            mid = str(vmt.materia_id)
            if mid not in mp:
                mp[mid] = []
            mp[mid].append({
                'pk': vmt.professor.pk,
                'nome': vmt.professor.papel.vinculo.usuario.nome,
            })

        materia_professores_json = json.dumps({
            'vinculos': mp,
            'todos': todos_professores,
        })

        return render(request, self.template_name, self._ctx(
            request,
            turma=turma,
            periodos=periodos,
            dias=_DIAS_SEMANA,
            grade=grade,
            materias=materias,
            materia_professores_json=materia_professores_json,
        ))


class SalvarSlotHorarioView(_DiretorMixin, View):
    def post(self, request, pk):
        from apps.professor.models import PerfilProfessor
        from apps.materia.models import Materia

        turma = get_object_or_404(Turma, pk=pk, escola=request.escola)
        periodo = get_object_or_404(PeriodoAula, pk=request.POST.get('periodo_id'), escola=request.escola)
        professor = get_object_or_404(PerfilProfessor, pk=request.POST.get('professor_id'), papel__vinculo__escola=request.escola)
        materia = get_object_or_404(Materia, pk=request.POST.get('materia_id'), escola=request.escola)
        try:
            dia = int(request.POST.get('dia_semana', 0))
        except (ValueError, TypeError):
            messages.error(request, 'Dia inválido.')
            return redirect('turma:horario', pk=turma.pk)

        try:
            with transaction.atomic():
                HorarioAula.objects.filter(
                    turma=turma, periodo=periodo, dia_semana=dia, ano_letivo=turma.ano_letivo,
                ).delete()
                HorarioAula.objects.create(
                    turma=turma, periodo=periodo, dia_semana=dia,
                    ano_letivo=turma.ano_letivo,
                    professor=professor, materia=materia, ativo=True,
                )
            messages.success(request, 'Horário salvo.')
        except IntegrityError:
            messages.error(request, f'{professor.usuario.nome} já tem aula neste horário com outra turma.')
        return redirect('turma:horario', pk=turma.pk)


class RemoverSlotHorarioView(_DiretorMixin, View):
    def post(self, request, pk, slot_pk):
        turma = get_object_or_404(Turma, pk=pk, escola=request.escola)
        slot = get_object_or_404(HorarioAula, pk=slot_pk, turma=turma)
        slot.delete()
        messages.success(request, 'Horário removido.')
        return redirect('turma:horario', pk=turma.pk)
