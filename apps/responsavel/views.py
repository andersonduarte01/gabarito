from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import CriarResponsavelForm, CriarSemAcessoForm, EditarResponsavelForm, VincularAlunoForm
from .models import PerfilResponsavel, VinculoResponsavelAluno
from .services import responsavel_service


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


class ListarResponsaveisView(_LeituraMixin, View):
    template_name = 'responsavel/lista.html'

    def get(self, request):
        escola = request.escola
        responsaveis = (
            PerfilResponsavel.objects
            .filter(vinculos_aluno__aluno__escola=escola)
            .distinct()
            .prefetch_related('vinculos_aluno__aluno')
            .order_by('nome')
        )
        return render(request, self.template_name, self._ctx(request, responsaveis=responsaveis))


class CriarResponsavelView(_DiretorMixin, View):
    template_name = 'responsavel/form_responsavel.html'

    def get(self, request):
        tipo = request.GET.get('tipo', 'acesso')
        form = CriarResponsavelForm() if tipo == 'acesso' else CriarSemAcessoForm()
        return render(request, self.template_name, self._ctx(request, form=form, tipo=tipo))

    def post(self, request):
        tipo = request.POST.get('tipo', 'acesso')
        form_cls = CriarResponsavelForm if tipo == 'acesso' else CriarSemAcessoForm
        form = form_cls(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                if tipo == 'acesso':
                    responsavel_service.criar(
                        escola=request.escola,
                        usuario_dados={'nome': cd['nome'], 'email': cd['email']},
                        perfil_dados={k: v for k, v in cd.items() if k not in ('nome', 'email')},
                    )
                else:
                    responsavel_service.criar_sem_acesso(perfil_dados=cd)
                messages.success(request, f'Responsável {cd["nome"]} cadastrado com sucesso.')
                return redirect('responsavel:lista')
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        return render(request, self.template_name, self._ctx(request, form=form, tipo=tipo))


class DetalheResponsavelView(_LeituraMixin, View):
    template_name = 'responsavel/detalhe.html'

    def get(self, request, pk):
        responsavel = get_object_or_404(
            PerfilResponsavel.objects.prefetch_related(
                'vinculos_aluno__aluno',
            ),
            pk=pk,
            vinculos_aluno__aluno__escola=request.escola,
        )
        vinculo_form = VincularAlunoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(
            request, responsavel=responsavel, vinculo_form=vinculo_form,
        ))


class EditarResponsavelView(_DiretorMixin, View):
    template_name = 'responsavel/form_responsavel.html'

    def _get(self, request, pk):
        return get_object_or_404(
            PerfilResponsavel,
            pk=pk, vinculos_aluno__aluno__escola=request.escola,
        )

    def get(self, request, pk):
        responsavel = self._get(request, pk)
        form = EditarResponsavelForm(instance=responsavel)
        return render(request, self.template_name, self._ctx(
            request, form=form, tipo='editar', responsavel=responsavel,
        ))

    def post(self, request, pk):
        responsavel = self._get(request, pk)
        form = EditarResponsavelForm(request.POST, instance=responsavel)
        if form.is_valid():
            responsavel_service.editar(responsavel, form.cleaned_data)
            messages.success(request, 'Responsável atualizado.')
            return redirect('responsavel:detalhe', pk=responsavel.pk)
        return render(request, self.template_name, self._ctx(
            request, form=form, tipo='editar', responsavel=responsavel,
        ))


class VincularAlunoView(_DiretorMixin, View):
    def post(self, request, pk):
        responsavel = get_object_or_404(
            PerfilResponsavel, pk=pk,
            vinculos_aluno__aluno__escola=request.escola,
        )
        form = VincularAlunoForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                responsavel_service.vincular_aluno(
                    perfil=responsavel,
                    aluno=cd['aluno'],
                    dados={
                        'parentesco':             cd['parentesco'],
                        'responsavel_principal':  cd['responsavel_principal'],
                        'responsavel_financeiro': cd['responsavel_financeiro'],
                    },
                )
                messages.success(request, f'Aluno {cd["aluno"].nome_completo} vinculado.')
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        else:
            messages.error(request, 'Dados inválidos.')
        return redirect('responsavel:detalhe', pk=responsavel.pk)


class DesvincularAlunoView(_DiretorMixin, View):
    def post(self, request, pk, vinculo_pk):
        responsavel = get_object_or_404(
            PerfilResponsavel, pk=pk,
            vinculos_aluno__aluno__escola=request.escola,
        )
        vinculo = get_object_or_404(VinculoResponsavelAluno, pk=vinculo_pk, responsavel=responsavel)
        responsavel_service.desvincular_aluno(vinculo)
        messages.success(request, 'Vínculo removido.')
        return redirect('responsavel:detalhe', pk=responsavel.pk)
