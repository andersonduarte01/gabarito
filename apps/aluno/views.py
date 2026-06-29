from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import CriarAlunoForm, EditarAlunoForm, MatriculaTurmaForm, TrocarTurmaForm
from .models import Aluno, MatriculaTurma
from .services import aluno_service


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


class CriarAlunoView(_DiretorMixin, View):
    template_name = 'aluno/form_aluno.html'

    def get(self, request):
        form = CriarAlunoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))

    def post(self, request):
        form = CriarAlunoForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                aluno_service.criar(request.escola, {
                    'nome_completo':   cd['nome_completo'],
                    'data_nascimento': cd.get('data_nascimento'),
                    'cpf':             cd.get('cpf', ''),
                    'rg':              cd.get('rg', ''),
                    'turma':           cd.get('turma'),
                    'ano_letivo':      cd.get('ano_letivo'),
                })
                messages.success(request, f'Aluno {cd["nome_completo"]} cadastrado com sucesso.')
                return redirect('aluno:lista')
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
        mat_form   = MatriculaTurmaForm(escola=request.escola)
        troca_form = TrocarTurmaForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(
            request, aluno=aluno, mat_form=mat_form, troca_form=troca_form,
        ))


class EditarAlunoView(_DiretorMixin, View):
    template_name = 'aluno/form_aluno.html'

    def _get_aluno(self, request, pk):
        return get_object_or_404(Aluno, pk=pk, escola=request.escola)

    def get(self, request, pk):
        aluno = self._get_aluno(request, pk)
        form  = EditarAlunoForm(instance=aluno)
        return render(request, self.template_name, self._ctx(request, form=form, editando=True, aluno=aluno))

    def post(self, request, pk):
        aluno = self._get_aluno(request, pk)
        form  = EditarAlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            aluno_service.editar(aluno, form.cleaned_data)
            messages.success(request, 'Aluno atualizado com sucesso.')
            return redirect('aluno:detalhe', pk=aluno.pk)
        return render(request, self.template_name, self._ctx(request, form=form, editando=True, aluno=aluno))


class DesativarAlunoView(_DiretorMixin, View):
    def post(self, request, pk):
        aluno = get_object_or_404(Aluno, pk=pk, escola=request.escola)
        aluno_service.desativar(aluno)
        messages.success(request, f'{aluno.nome_completo} foi desativado.')
        return redirect('aluno:lista')


class ReativarAlunoView(_DiretorMixin, View):
    def post(self, request, pk):
        aluno = get_object_or_404(Aluno, pk=pk, escola=request.escola)
        aluno_service.reativar(aluno)
        messages.success(request, f'{aluno.nome_completo} foi reativado.')
        return redirect('aluno:lista')


class MatricularView(_DiretorMixin, View):
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


class TrocarTurmaView(_DiretorMixin, View):
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


class TransferirView(_DiretorMixin, View):
    def post(self, request, mat_pk):
        matricula = get_object_or_404(
            MatriculaTurma, pk=mat_pk, aluno__escola=request.escola, ativo=True,
        )
        aluno_service.transferir(matricula)
        messages.success(request, f'{matricula.aluno.nome_completo} transferido(a).')
        return redirect('aluno:lista')


class EvadiemView(_DiretorMixin, View):
    def post(self, request, mat_pk):
        matricula = get_object_or_404(
            MatriculaTurma, pk=mat_pk, aluno__escola=request.escola, ativo=True,
        )
        aluno_service.evadir(matricula)
        messages.success(request, f'{matricula.aluno.nome_completo} marcado(a) como evadido(a).')
        return redirect('aluno:lista')


class ConcluirView(_DiretorMixin, View):
    def post(self, request, mat_pk):
        matricula = get_object_or_404(
            MatriculaTurma, pk=mat_pk, aluno__escola=request.escola, ativo=True,
        )
        aluno_service.concluir(matricula)
        messages.success(request, f'{matricula.aluno.nome_completo} marcado(a) como concluinte.')
        return redirect('aluno:detalhe', pk=matricula.aluno_id)
