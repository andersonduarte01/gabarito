from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.core.services.usuario_service import editar as editar_usuario, trocar_email
from .forms import (
    AlterarSenhaColaboradorForm,
    CriarColaboradorForm,
    EditarColaboradorForm,
    EditarMeuPerfilColaboradorForm,
    EnderecoPerfilForm,
    FuncaoEscolarForm,
    TrocarMinhaSenhaForm,
)
from .models import FuncaoEscolar, PerfilColaborador
from .services import colaborador_service, funcao_service


class _FuncionarioMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo != 'FUNCIONARIO':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


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
# Colaboradores
# ---------------------------------------------------------------------------

class ListarColaboradoresView(_LeituraMixin, View):
    template_name = 'colaborador/lista.html'

    def get(self, request):
        escola = request.escola
        colaboradores = (
            PerfilColaborador.objects
            .filter(papel__vinculo__escola=escola)
            .select_related('papel__vinculo__usuario', 'funcao')
            .order_by('papel__ativo', 'papel__vinculo__usuario__nome')
        )
        return render(request, self.template_name, self._ctx(
            request, colaboradores=colaboradores,
        ))


class CriarColaboradorView(_DiretorMixin, View):
    template_name = 'colaborador/form_colaborador.html'

    def get(self, request):
        form = CriarColaboradorForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=False,
        ))

    def post(self, request):
        form = CriarColaboradorForm(request.POST, request.FILES, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                colaborador_service.criar(
                    escola=request.escola,
                    usuario_dados={'nome': cd['nome'], 'email': cd['email'], 'senha': cd['senha']},
                    perfil_dados={k: v for k, v in cd.items() if k not in ('nome', 'email', 'senha', 'confirmar_senha')},
                    criado_por=request.user,
                )
                messages.success(request, 'Colaborador cadastrado com sucesso.')
                return redirect('colaborador:lista')
            except Exception as exc:
                messages.error(request, f'Erro ao cadastrar: {exc}')
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=False,
        ))


class DetalheColaboradorView(_LeituraMixin, View):
    template_name = 'colaborador/detalhe.html'

    def get(self, request, pk):
        perfil = get_object_or_404(
            PerfilColaborador.objects.select_related(
                'papel__vinculo__usuario', 'funcao', 'endereco'
            ),
            pk=pk, papel__vinculo__escola=request.escola,
        )
        return render(request, self.template_name, self._ctx(request, perfil=perfil))


class EditarColaboradorView(_DiretorMixin, View):
    template_name = 'colaborador/form_colaborador.html'

    def _get_perfil(self, request, pk):
        return get_object_or_404(
            PerfilColaborador, pk=pk, papel__vinculo__escola=request.escola,
        )

    def get(self, request, pk):
        perfil = self._get_perfil(request, pk)
        form = EditarColaboradorForm(
            instance=perfil, escola=request.escola, usuario=perfil.usuario,
        )
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, perfil=perfil,
        ))

    def post(self, request, pk):
        perfil = self._get_perfil(request, pk)
        form = EditarColaboradorForm(
            request.POST, request.FILES, instance=perfil, escola=request.escola, usuario=perfil.usuario,
        )
        if form.is_valid():
            novo_nome  = form.cleaned_data.pop('nome')
            novo_email = form.cleaned_data.pop('email')
            editar_usuario(perfil.usuario, {'nome': novo_nome})
            if novo_email != perfil.usuario.email:
                trocar_email(perfil.usuario, novo_email)
            colaborador_service.editar(perfil, form.cleaned_data)
            messages.success(request, 'Colaborador atualizado com sucesso.')
            return redirect('colaborador:detalhe', pk=perfil.pk)
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, perfil=perfil,
        ))


class AlterarSenhaColaboradorView(_DiretorMixin, View):
    template_name = 'colaborador/alterar_senha.html'

    def _get_perfil(self, request, pk):
        return get_object_or_404(
            PerfilColaborador, pk=pk, papel__vinculo__escola=request.escola,
        )

    def get(self, request, pk):
        perfil = self._get_perfil(request, pk)
        form = AlterarSenhaColaboradorForm()
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))

    def post(self, request, pk):
        perfil = self._get_perfil(request, pk)
        form = AlterarSenhaColaboradorForm(request.POST)
        if form.is_valid():
            perfil.usuario.set_password(form.cleaned_data['nova_senha'])
            perfil.usuario.save(update_fields=['password'])
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('colaborador:detalhe', pk=perfil.pk)
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))


class DesativarColaboradorView(_DiretorMixin, View):
    def post(self, request, pk):
        perfil = get_object_or_404(
            PerfilColaborador, pk=pk, papel__vinculo__escola=request.escola,
        )
        colaborador_service.desativar(perfil.papel, desativado_por=request.user)
        messages.success(request, f'{perfil.usuario.nome} foi desativado.')
        return redirect('colaborador:lista')


class ReativarColaboradorView(_DiretorMixin, View):
    def post(self, request, pk):
        perfil = get_object_or_404(
            PerfilColaborador, pk=pk, papel__vinculo__escola=request.escola,
        )
        colaborador_service.reativar(perfil.papel)
        messages.success(request, f'{perfil.usuario.nome} foi reativado.')
        return redirect('colaborador:lista')


# ---------------------------------------------------------------------------
# Funções Escolares
# ---------------------------------------------------------------------------

class ListarFuncoesView(_DiretorMixin, View):
    template_name = 'colaborador/lista_funcoes.html'

    def get(self, request):
        funcoes = FuncaoEscolar.objects.filter(escola=request.escola).order_by('nome')
        return render(request, self.template_name, self._ctx(request, funcoes=funcoes))


class CriarFuncaoView(_DiretorMixin, View):
    template_name = 'colaborador/form_funcao.html'

    def get(self, request):
        form = FuncaoEscolarForm()
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))

    def post(self, request):
        form = FuncaoEscolarForm(request.POST)
        if form.is_valid():
            try:
                funcao_service.criar(request.escola, form.cleaned_data['nome'])
                messages.success(request, 'Função criada.')
                return redirect('colaborador:funcoes')
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))


class EditarFuncaoView(_DiretorMixin, View):
    template_name = 'colaborador/form_funcao.html'

    def _get_funcao(self, request, pk):
        return get_object_or_404(FuncaoEscolar, pk=pk, escola=request.escola)

    def get(self, request, pk):
        funcao = self._get_funcao(request, pk)
        form = FuncaoEscolarForm(initial={'nome': funcao.nome})
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, funcao=funcao,
        ))

    def post(self, request, pk):
        funcao = self._get_funcao(request, pk)
        form = FuncaoEscolarForm(request.POST)
        if form.is_valid():
            funcao_service.editar(funcao, form.cleaned_data['nome'])
            messages.success(request, 'Função atualizada.')
            return redirect('colaborador:funcoes')
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, funcao=funcao,
        ))


class DesativarFuncaoView(_DiretorMixin, View):
    def post(self, request, pk):
        funcao = get_object_or_404(FuncaoEscolar, pk=pk, escola=request.escola)
        funcao_service.desativar(funcao)
        messages.success(request, f'Função "{funcao.nome}" desativada.')
        return redirect('colaborador:funcoes')


class ReativarFuncaoView(_DiretorMixin, View):
    def post(self, request, pk):
        funcao = get_object_or_404(FuncaoEscolar, pk=pk, escola=request.escola)
        funcao_service.reativar(funcao)
        messages.success(request, f'Função "{funcao.nome}" reativada.')
        return redirect('colaborador:funcoes')


class PermissoesFuncaoView(_DiretorMixin, View):
    template_name = 'colaborador/permissoes_funcao.html'

    def _get_funcao(self, request, pk):
        return get_object_or_404(FuncaoEscolar, pk=pk, escola=request.escola)

    def get(self, request, pk):
        from .models import MODULOS_COLABORADOR
        from .services.permissao_service import get_modulos
        funcao = self._get_funcao(request, pk)
        ativos = get_modulos(funcao)
        return render(request, self.template_name, self._ctx(
            request, funcao=funcao, modulos=MODULOS_COLABORADOR, ativos=ativos,
        ))

    def post(self, request, pk):
        from .models import MODULOS_COLABORADOR
        from .services.permissao_service import set_permissoes
        funcao = self._get_funcao(request, pk)
        chaves_validas = {m[0] for m in MODULOS_COLABORADOR}
        selecionados = [m for m in request.POST.getlist('modulos') if m in chaves_validas]
        set_permissoes(funcao, selecionados)
        messages.success(request, f'Permissões de "{funcao.nome}" atualizadas.')
        return redirect('colaborador:funcoes')


# ---------------------------------------------------------------------------
# Portal do Funcionário
# ---------------------------------------------------------------------------

class DashboardFuncionarioView(_FuncionarioMixin, View):
    template_name = 'colaborador/dashboard.html'

    def get(self, request):
        escola = request.escola

        from apps.aluno.models import MatriculaTurma
        from apps.turma.models import Turma
        from apps.professor.models import PerfilProfessor
        from apps.financeiro.models import CobrancaAluno, StatusCobranca
        from apps.comunicado.models import Comunicado
        from apps.agenda.models import Evento
        from apps.ano_letivo.models import AnoLetivo, StatusAnoLetivo
        from django.utils import timezone

        total_alunos = MatriculaTurma.objects.filter(turma__escola=escola, ativo=True).count()
        total_turmas = Turma.objects.filter(escola=escola, ativo=True).count()
        total_professores = (
            PerfilProfessor.objects
            .filter(papel__vinculo__escola=escola, papel__ativo=True)
            .count()
        )
        cobrancas_pendentes = CobrancaAluno.objects.filter(
            aluno__escola=escola,
            status__in=[StatusCobranca.PENDENTE, StatusCobranca.VENCIDO],
        ).count()

        ano_letivo = (
            AnoLetivo.objects
            .filter(escola=escola, status=StatusAnoLetivo.EM_ANDAMENTO)
            .first()
        )

        comunicados_recentes = (
            Comunicado.objects
            .filter(escola=escola, publicada=True)
            .order_by('-criado_em')[:5]
        )

        hoje = timezone.localdate()
        proximos_eventos = (
            Evento.objects
            .filter(escola=escola, publicada=True, data_inicio__gte=hoje)
            .order_by('data_inicio')[:4]
        )

        try:
            perfil = request.papel.perfil_colaborador
        except PerfilColaborador.DoesNotExist:
            perfil = None

        return render(request, self.template_name, self._ctx(
            request,
            active_nav='dashboard',
            perfil=perfil,
            ano_letivo=ano_letivo,
            total_alunos=total_alunos,
            total_turmas=total_turmas,
            total_professores=total_professores,
            cobrancas_pendentes=cobrancas_pendentes,
            comunicados_recentes=comunicados_recentes,
            proximos_eventos=proximos_eventos,
        ))


class MeuPerfilColaboradorView(_FuncionarioMixin, View):
    template_name = 'colaborador/meu_perfil.html'

    def get(self, request):
        try:
            perfil = request.papel.perfil_colaborador
        except PerfilColaborador.DoesNotExist:
            perfil = None
        return render(request, self.template_name, self._ctx(
            request, active_nav='perfil', perfil=perfil,
        ))


class EditarMeuPerfilView(_FuncionarioMixin, View):
    template_name = 'colaborador/editar_meu_perfil.html'

    def _get_perfil(self, request):
        try:
            return request.papel.perfil_colaborador
        except PerfilColaborador.DoesNotExist:
            return None

    def get(self, request):
        perfil = self._get_perfil(request)
        if perfil is None:
            messages.error(request, 'Perfil não encontrado. Solicite ao diretor que complete seu cadastro.')
            return redirect('colaborador:meu_perfil')
        form = EditarMeuPerfilColaboradorForm(instance=perfil, usuario=request.user)
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))

    def post(self, request):
        perfil = self._get_perfil(request)
        if perfil is None:
            return redirect('colaborador:meu_perfil')
        form = EditarMeuPerfilColaboradorForm(
            request.POST, request.FILES, instance=perfil, usuario=request.user,
        )
        if form.is_valid():
            novo_nome  = form.cleaned_data.pop('nome')
            novo_email = form.cleaned_data.pop('email')
            editar_usuario(request.user, {'nome': novo_nome})
            if novo_email != request.user.email:
                trocar_email(request.user, novo_email)
            colaborador_service.editar(perfil, form.cleaned_data)
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('colaborador:meu_perfil')
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))


class EditarMeuEnderecoView(_FuncionarioMixin, View):
    template_name = 'colaborador/editar_meu_endereco.html'

    def _get_perfil(self, request):
        try:
            return request.papel.perfil_colaborador
        except PerfilColaborador.DoesNotExist:
            return None

    def get(self, request):
        perfil = self._get_perfil(request)
        if perfil is None:
            return redirect('colaborador:meu_perfil')
        form = EnderecoPerfilForm(instance=perfil.endereco)
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))

    def post(self, request):
        perfil = self._get_perfil(request)
        if perfil is None:
            return redirect('colaborador:meu_perfil')
        form = EnderecoPerfilForm(request.POST, instance=perfil.endereco)
        if form.is_valid():
            colaborador_service.salvar_endereco(perfil, form.cleaned_data)
            messages.success(request, 'Endereço atualizado.')
            return redirect('colaborador:meu_perfil')
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))


class TrocarMinhaSenhaView(_FuncionarioMixin, View):
    template_name = 'colaborador/trocar_minha_senha.html'

    def get(self, request):
        form = TrocarMinhaSenhaForm()
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = TrocarMinhaSenhaForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['senha_atual']):
                form.add_error('senha_atual', 'Senha atual incorreta.')
                return render(request, self.template_name, self._ctx(request, form=form))
            request.user.set_password(form.cleaned_data['nova_senha'])
            request.user.save(update_fields=['password'])
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('colaborador:meu_perfil')
        return render(request, self.template_name, self._ctx(request, form=form))
