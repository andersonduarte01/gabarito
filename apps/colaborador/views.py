from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.core.services.usuario_service import editar as editar_usuario, trocar_email
from .forms import AlterarSenhaColaboradorForm, CriarColaboradorForm, EditarColaboradorForm, EnderecoPerfilForm, FuncaoEscolarForm
from .models import FuncaoEscolar, PerfilColaborador
from .services import colaborador_service, funcao_service


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
