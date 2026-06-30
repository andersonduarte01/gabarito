from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.core.services.usuario_service import editar as editar_usuario
from apps.core.services.usuario_service import trocar_email

from .forms import CriarDiretorForm, EditarPerfilDiretorForm, EnderecoPerfilForm
from .models import PerfilDiretor
from .services.diretor_service import criar, desativar, editar, salvar_endereco


class DiretorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo != 'DIRETOR':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {
            'usuario': request.user,
            'escola':  request.escola,
            'papel':   request.papel,
            **extra,
        }


class DashboardView(DiretorRequiredMixin, View):
    template_name = 'diretor/dashboard.html'

    def get(self, request):
        escola = request.escola

        # KPIs — expandidos conforme módulos são implementados
        from apps.colaborador.models import PerfilColaborador
        from apps.professor.models import PerfilProfessor
        from apps.turma.models import Turma
        from apps.aluno.models import MatriculaTurma
        total_alunos      = MatriculaTurma.objects.filter(turma__escola=escola, ativo=True).count()
        total_turmas      = (
            Turma.objects.filter(escola=escola, ativo=True).count()
        )
        total_professores = (
            PerfilProfessor.objects
            .filter(papel__vinculo__escola=escola, papel__ativo=True)
            .count()
        )
        total_colaboradores = (
            PerfilColaborador.objects
            .filter(papel__vinculo__escola=escola, papel__ativo=True)
            .count()
        )

        from apps.ano_letivo.models import AnoLetivo, StatusAnoLetivo
        ano_letivo = (
            AnoLetivo.objects
            .filter(escola=escola, status=StatusAnoLetivo.EM_ANDAMENTO)
            .first()
        )

        diretores = (
            PerfilDiretor.objects
            .filter(papel__vinculo__escola=escola, papel__ativo=True)
            .select_related('papel__vinculo__usuario')
            .order_by('cargo', 'papel__vinculo__usuario__nome')
        )

        try:
            assinatura = escola.assinatura
        except Exception:
            assinatura = None

        grace_dias = getattr(request, 'grace_dias_restantes', None)

        return render(request, self.template_name, self._ctx(
            request,
            total_alunos=total_alunos,
            total_turmas=total_turmas,
            total_professores=total_professores,
            total_colaboradores=total_colaboradores,
            ano_letivo=ano_letivo,
            diretores=diretores,
            assinatura=assinatura,
            grace_dias=grace_dias,
        ))


class MeuPerfilView(DiretorRequiredMixin, View):
    template_name = 'diretor/meu_perfil.html'

    def get(self, request):
        try:
            perfil = request.papel.perfil_diretor
        except PerfilDiretor.DoesNotExist:
            perfil = None
        return render(request, self.template_name, self._ctx(request, perfil=perfil))


class EditarPerfilView(DiretorRequiredMixin, View):
    template_name = 'diretor/editar_perfil.html'

    def _get_perfil(self, request):
        try:
            return request.papel.perfil_diretor
        except PerfilDiretor.DoesNotExist:
            return None

    def get(self, request):
        perfil = self._get_perfil(request)
        form   = EditarPerfilDiretorForm(instance=perfil, usuario=request.user)
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))

    def post(self, request):
        perfil = self._get_perfil(request)
        form   = EditarPerfilDiretorForm(request.POST, request.FILES, instance=perfil, usuario=request.user)
        if form.is_valid():
            novo_nome  = form.cleaned_data.pop('nome')
            novo_email = form.cleaned_data.pop('email')

            editar_usuario(request.user, {'nome': novo_nome})
            if novo_email != request.user.email:
                trocar_email(request.user, novo_email)

            if perfil:
                editar(perfil, form.cleaned_data)
            else:
                novo = form.save(commit=False)
                novo.papel = request.papel
                novo.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('diretor:meu_perfil')
        return render(request, self.template_name, self._ctx(request, form=form, perfil=perfil))


class EditarEnderecoPerfilView(DiretorRequiredMixin, View):
    template_name = 'diretor/editar_endereco.html'

    def _get_perfil(self, request):
        try:
            return request.papel.perfil_diretor
        except PerfilDiretor.DoesNotExist:
            return None

    def get(self, request):
        perfil   = self._get_perfil(request)
        endereco = perfil.endereco if perfil else None
        form     = EnderecoPerfilForm(instance=endereco)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        perfil = self._get_perfil(request)
        if perfil is None:
            messages.error(request, 'Complete seu perfil antes de adicionar o endereço.')
            return redirect('diretor:editar_perfil')
        endereco = perfil.endereco
        form     = EnderecoPerfilForm(request.POST, instance=endereco)
        if form.is_valid():
            salvar_endereco(perfil, form.cleaned_data)
            messages.success(request, 'Endereço atualizado.')
            return redirect('diretor:meu_perfil')
        return render(request, self.template_name, self._ctx(request, form=form))


class ListarDiretoresView(DiretorRequiredMixin, View):
    template_name = 'diretor/listar_diretores.html'

    def get(self, request):
        escola = request.escola
        diretores = (
            PerfilDiretor.objects
            .filter(papel__vinculo__escola=escola)
            .select_related('papel__vinculo__usuario')
            .order_by('cargo', 'papel__vinculo__usuario__nome')
        )
        return render(request, self.template_name, self._ctx(request, diretores=diretores))


class CriarDiretorView(DiretorRequiredMixin, View):
    template_name = 'diretor/form_diretor.html'

    def get(self, request):
        form = CriarDiretorForm()
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = CriarDiretorForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                usuario_dados = {
                    'nome':  form.cleaned_data['nome'],
                    'email': form.cleaned_data['email'],
                    'senha': form.cleaned_data['senha'],
                }
                perfil_dados = {k: v for k, v in form.cleaned_data.items()
                                if k not in ('nome', 'email', 'senha', 'confirmar_senha')}
                criar(
                    escola=request.escola,
                    usuario_dados=usuario_dados,
                    perfil_dados=perfil_dados,
                    criado_por=request.user,
                )
                messages.success(request, 'Diretor cadastrado com sucesso.')
                return redirect('diretor:listar_diretores')
            except Exception as exc:
                messages.error(request, f'Erro ao cadastrar diretor: {exc}')
        return render(request, self.template_name, self._ctx(request, form=form))


class DesativarDiretorView(DiretorRequiredMixin, View):
    def post(self, request, pk):
        perfil = get_object_or_404(
            PerfilDiretor,
            pk=pk,
            papel__vinculo__escola=request.escola,
        )
        if perfil.papel == request.papel:
            messages.error(request, 'Você não pode desativar a si mesmo.')
            return redirect('diretor:listar_diretores')
        desativar(perfil.papel, desativado_por=request.user)
        messages.success(request, f'{perfil.usuario.nome} foi desativado.')
        return redirect('diretor:listar_diretores')
