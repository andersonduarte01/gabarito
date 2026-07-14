from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.core.services.usuario_service import editar as editar_usuario, trocar_email
from .forms import AlterarSenhaProfessorForm, CriarProfessorForm, EditarProfessorForm, EnderecoPerfilForm, FormacaoAcademicaForm
from .models import FormacaoAcademica, PerfilProfessor
from .services import professor_service


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


class _ProfessorMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo != 'PROFESSOR':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class DashboardProfessorView(_ProfessorMixin, View):
    template_name = 'professor/dashboard.html'

    def get(self, request):
        import datetime
        from apps.turma.models import ProfessorMateriaTurma
        from apps.aluno.models import MatriculaTurma, SituacaoMatricula
        from apps.ano_letivo.models import AnoLetivo
        from apps.comunicado.models import Comunicado
        from apps.agenda.models import Evento

        try:
            perfil = request.papel.perfil_professor
        except Exception:
            perfil = None

        ano_letivo = AnoLetivo.objects.filter(escola=request.escola, status='EM_ANDAMENTO').first()

        atribuicoes = ProfessorMateriaTurma.objects.none()
        total_turmas = 0
        total_materias = 0
        total_alunos = 0

        if perfil and ano_letivo:
            atribuicoes = (
                ProfessorMateriaTurma.objects
                .filter(professor=perfil, ano_letivo=ano_letivo, ativo=True)
                .select_related('turma', 'materia')
                .order_by('turma__nome', 'materia__nome')
            )
            turma_ids = atribuicoes.values_list('turma_id', flat=True).distinct()
            total_turmas = turma_ids.count()
            total_materias = atribuicoes.values('materia').distinct().count()
            total_alunos = (
                MatriculaTurma.objects
                .filter(
                    turma_id__in=turma_ids,
                    ano_letivo=ano_letivo,
                    situacao=SituacaoMatricula.MATRICULADO,
                )
                .values('aluno').distinct().count()
            )

        comunicados_recentes = (
            Comunicado.objects
            .filter(escola=request.escola)
            .order_by('-criado_em')[:5]
        )
        proximos_eventos = (
            Evento.objects
            .filter(escola=request.escola, data_inicio__gte=datetime.date.today())
            .order_by('data_inicio')[:4]
        )

        return render(request, self.template_name, self._ctx(
            request,
            perfil=perfil,
            ano_letivo=ano_letivo,
            total_turmas=total_turmas,
            total_materias=total_materias,
            total_alunos=total_alunos,
            atribuicoes=atribuicoes,
            comunicados_recentes=comunicados_recentes,
            proximos_eventos=proximos_eventos,
            active_nav='dashboard',
        ))


class MeuPerfilProfessorView(_ProfessorMixin, View):
    template_name = 'professor/meu_perfil.html'

    def get(self, request):
        try:
            perfil = request.papel.perfil_professor
        except Exception:
            perfil = None
        return render(request, self.template_name, self._ctx(
            request, perfil=perfil, active_nav='perfil',
        ))


class ListarProfessoresView(_LeituraMixin, View):
    template_name = 'professor/lista.html'

    def get(self, request):
        professores = (
            PerfilProfessor.objects
            .filter(papel__vinculo__escola=request.escola)
            .select_related('papel__vinculo__usuario')
            .order_by('papel__ativo', 'papel__vinculo__usuario__nome')
        )
        return render(request, self.template_name, self._ctx(request, professores=professores))


class CriarProfessorView(_DiretorMixin, View):
    template_name = 'professor/form_professor.html'

    def get(self, request):
        form = CriarProfessorForm()
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))

    def post(self, request):
        form = CriarProfessorForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                professor_service.criar(
                    escola=request.escola,
                    usuario_dados={'nome': cd['nome'], 'email': cd['email'], 'senha': cd['senha']},
                    perfil_dados={k: v for k, v in cd.items() if k not in ('nome', 'email', 'senha', 'confirmar_senha')},
                    criado_por=request.user,
                )
                messages.success(request, 'Professor cadastrado com sucesso.')
                return redirect('professor:lista')
            except Exception as exc:
                messages.error(request, f'Erro ao cadastrar: {exc}')
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))


class DetalheProfessorView(_LeituraMixin, View):
    template_name = 'professor/detalhe.html'

    def get(self, request, pk):
        perfil = get_object_or_404(
            PerfilProfessor.objects.select_related(
                'papel__vinculo__usuario', 'endereco'
            ).prefetch_related(
                'formacoes',
                'professor_materia_turmas__materia',
                'professor_materia_turmas__turma__ano_letivo',
                'professor_materia_turmas__turma__serie',
            ),
            pk=pk, papel__vinculo__escola=request.escola,
        )
        formacao_form = FormacaoAcademicaForm()
        return render(request, self.template_name, self._ctx(
            request, perfil=perfil, formacao_form=formacao_form,
        ))


class EditarProfessorView(_DiretorMixin, View):
    template_name = 'professor/form_professor.html'

    def _get_perfil(self, request, pk):
        return get_object_or_404(
            PerfilProfessor, pk=pk, papel__vinculo__escola=request.escola,
        )

    def get(self, request, pk):
        perfil = self._get_perfil(request, pk)
        form = EditarProfessorForm(instance=perfil, usuario=perfil.usuario)
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, perfil=perfil,
        ))

    def post(self, request, pk):
        perfil = self._get_perfil(request, pk)
        form = EditarProfessorForm(request.POST, request.FILES, instance=perfil, usuario=perfil.usuario)
        if form.is_valid():
            novo_nome  = form.cleaned_data.pop('nome')
            novo_email = form.cleaned_data.pop('email')
            editar_usuario(perfil.usuario, {'nome': novo_nome})
            if novo_email != perfil.usuario.email:
                trocar_email(perfil.usuario, novo_email)
            professor_service.editar(perfil, form.cleaned_data)
            messages.success(request, 'Professor atualizado.')
            return redirect('professor:detalhe', pk=perfil.pk)
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, perfil=perfil,
        ))


class AlterarSenhaProfessorView(_DiretorMixin, View):
    template_name = 'professor/alterar_senha.html'

    def _get_perfil(self, request, pk):
        return get_object_or_404(
            PerfilProfessor, pk=pk, papel__vinculo__escola=request.escola,
        )

    def get(self, request, pk):
        perfil = self._get_perfil(request, pk)
        form = AlterarSenhaProfessorForm()
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))

    def post(self, request, pk):
        perfil = self._get_perfil(request, pk)
        form = AlterarSenhaProfessorForm(request.POST)
        if form.is_valid():
            perfil.usuario.set_password(form.cleaned_data['nova_senha'])
            perfil.usuario.save(update_fields=['password'])
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('professor:detalhe', pk=perfil.pk)
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))


class DesativarProfessorView(_DiretorMixin, View):
    def post(self, request, pk):
        perfil = get_object_or_404(
            PerfilProfessor, pk=pk, papel__vinculo__escola=request.escola,
        )
        professor_service.desativar(perfil.papel, desativado_por=request.user)
        messages.success(request, f'{perfil.usuario.nome} foi desativado.')
        return redirect('professor:lista')


class ReativarProfessorView(_DiretorMixin, View):
    def post(self, request, pk):
        perfil = get_object_or_404(
            PerfilProfessor, pk=pk, papel__vinculo__escola=request.escola,
        )
        professor_service.reativar(perfil.papel)
        messages.success(request, f'{perfil.usuario.nome} foi reativado.')
        return redirect('professor:lista')


class AdicionarFormacaoView(_DiretorMixin, View):
    def post(self, request, pk):
        perfil = get_object_or_404(
            PerfilProfessor, pk=pk, papel__vinculo__escola=request.escola,
        )
        form = FormacaoAcademicaForm(request.POST)
        if form.is_valid():
            professor_service.adicionar_formacao(perfil, form.cleaned_data)
            messages.success(request, 'Formação adicionada.')
        else:
            messages.error(request, 'Dados de formação inválidos.')
        return redirect('professor:detalhe', pk=perfil.pk)


class RemoverFormacaoView(_DiretorMixin, View):
    def post(self, request, pk, formacao_pk):
        perfil = get_object_or_404(
            PerfilProfessor, pk=pk, papel__vinculo__escola=request.escola,
        )
        formacao = get_object_or_404(FormacaoAcademica, pk=formacao_pk, professor=perfil)
        professor_service.remover_formacao(formacao)
        messages.success(request, 'Formação removida.')
        return redirect('professor:detalhe', pk=perfil.pk)


class GerenciarVinculosView(_DiretorMixin, View):
    template_name = 'professor/vinculos.html'

    def _get_perfil(self, request, pk):
        return get_object_or_404(
            PerfilProfessor, pk=pk, papel__vinculo__escola=request.escola,
        )

    def get(self, request, pk):
        from apps.turma.models import Turma, ProfessorMateriaTurma
        from apps.materia.models import Materia
        from apps.ano_letivo.models import AnoLetivo

        perfil = self._get_perfil(request, pk)
        anos = AnoLetivo.objects.filter(escola=request.escola).order_by('-ano')

        ano_id = request.GET.get('ano')
        if ano_id:
            ano = get_object_or_404(AnoLetivo, pk=ano_id, escola=request.escola)
        else:
            ano = anos.filter(status='EM_ANDAMENTO').first() or anos.first()

        if not ano:
            return render(request, self.template_name, self._ctx(
                request, perfil=perfil, anos=anos, ano=None, grade=[], materias=[],
            ))

        turmas = (
            Turma.objects
            .filter(escola=request.escola, ano_letivo=ano, ativo=True)
            .select_related('serie')
            .order_by('serie__ordem', 'nome')
        )
        materias = list(
            Materia.objects.filter(escola=request.escola, ativo=True).order_by('nome')
        )

        all_vmts = (
            ProfessorMateriaTurma.objects
            .filter(turma__in=turmas, ano_letivo=ano)
            .select_related('professor__papel__vinculo__usuario')
        )
        mine = set()
        taken = {}
        for vmt in all_vmts:
            key = (vmt.turma_id, vmt.materia_id)
            if vmt.professor_id == perfil.pk:
                mine.add(key)
            else:
                taken[key] = vmt.professor.papel.vinculo.usuario.nome

        grade = []
        for turma in turmas:
            cells = []
            for materia in materias:
                key = (turma.pk, materia.pk)
                if key in mine:
                    cells.append({'materia': materia, 'state': 'mine', 'by': None})
                elif key in taken:
                    cells.append({'materia': materia, 'state': 'taken', 'by': taken[key]})
                else:
                    cells.append({'materia': materia, 'state': 'free', 'by': None})
            grade.append({'turma': turma, 'cells': cells})

        return render(request, self.template_name, self._ctx(
            request, perfil=perfil, anos=anos, ano=ano, materias=materias, grade=grade,
        ))

    def post(self, request, pk):
        from apps.turma.models import Turma, ProfessorMateriaTurma
        from apps.ano_letivo.models import AnoLetivo

        perfil = self._get_perfil(request, pk)
        ano = get_object_or_404(AnoLetivo, pk=request.POST.get('ano_id'), escola=request.escola)

        turmas = Turma.objects.filter(escola=request.escola, ano_letivo=ano, ativo=True)
        valid_turma_ids = set(turmas.values_list('pk', flat=True))

        checked = set()
        for v in request.POST.getlist('vmt'):
            try:
                t_id, m_id = v.split('_')
                t_id, m_id = int(t_id), int(m_id)
                if t_id in valid_turma_ids:
                    checked.add((t_id, m_id))
            except (ValueError, AttributeError):
                pass

        current_qs = ProfessorMateriaTurma.objects.filter(
            professor=perfil, turma__in=turmas, ano_letivo=ano,
        )
        current_mine = {(v.turma_id, v.materia_id): v for v in current_qs}

        for turma_id, materia_id in checked - set(current_mine):
            already_taken = ProfessorMateriaTurma.objects.filter(
                turma_id=turma_id, materia_id=materia_id, ano_letivo=ano,
            ).exclude(professor=perfil).exists()
            if not already_taken:
                ProfessorMateriaTurma.objects.create(
                    professor=perfil,
                    materia_id=materia_id,
                    turma_id=turma_id,
                    ano_letivo=ano,
                )

        for key in set(current_mine) - checked:
            current_mine[key].delete()

        messages.success(request, 'Vínculos atualizados com sucesso.')
        return redirect('professor:detalhe', pk=perfil.pk)
