from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.turma.models import Turma
from apps.turma.forms import TurmaForm
from apps.turma.services import turma_service


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
