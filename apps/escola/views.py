from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, RedirectView

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from apps.core.views import BaseDashboardView
from .forms import EscolaForm, EnderecoEscolarForm
from .models import UnidadeEscolar, EnderecoEscolar
from .serializers import (
    UnidadeEscolarSerializer,
    UnidadeEscolarSerializerEdit,
    EnderecoEscolarSerializer,
)


# ---------------------------------------------------------------------------
# Roteamento inicial
# ---------------------------------------------------------------------------

class RedirecionarDashboard(LoginRequiredMixin, RedirectView):
    """
    Ponto de entrada após o login.
    Redireciona para o dashboard correto conforme o tipo de vínculo do usuário.
    Se não houver escola na sessão, manda para a tela de seleção.
    """
    def get_redirect_url(self, *args, **kwargs):
        escola = getattr(self.request, 'escola', None)
        if escola is None:
            return reverse_lazy('escola:selecionar')
        return self.request.user.get_dashboard_url(escola)


# ---------------------------------------------------------------------------
# Seleção de escola (multi-tenant)
# ---------------------------------------------------------------------------

class SelecionarEscola(LoginRequiredMixin, TemplateView):
    """
    Exibe as escolas vinculadas ao usuário para ele escolher com qual deseja operar.
    Chamada automaticamente pelo EscolaMiddleware quando o usuário tem múltiplos vínculos
    ou quando escola_id não está na sessão.
    """
    template_name = 'escola/selecionar_escola.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vinculos'] = (
            UsuarioEscola.objects
            .filter(usuario=self.request.user, ativo=True)
            .select_related('escola')
            .order_by('escola__nome_escola')
        )
        return context

    def post(self, request, *args, **kwargs):
        escola_id = request.POST.get('escola_id')
        if not escola_id:
            return redirect('escola:selecionar')

        vinculo = (
            UsuarioEscola.objects
            .select_related('escola')
            .filter(usuario=request.user, escola_id=escola_id, ativo=True)
            .first()
        )
        if not vinculo:
            return redirect('escola:selecionar')

        request.session['escola_id'] = vinculo.escola.pk
        return HttpResponseRedirect(request.user.get_dashboard_url(vinculo.escola))


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------

class DashAdmin(BaseDashboardView):
    """
    Painel do administrador — visão de todas as escolas do sistema.
    Acesso: somente ADMIN.
    """
    template_name = 'escola/administrador_dash.html'
    tipo_permitido = [UsuarioEscola.ADMIN]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escolas'] = (
            UnidadeEscolar.objects
            .filter(ativo=True)
            .prefetch_related('anos_letivos', 'vinculos')
            .order_by('nome_escola')
        )
        return context


class DashEscola(BaseDashboardView):
    """
    Painel da escola — visão do diretor e colaborador.
    Exibe salas, ano letivo corrente e resumo da escola.
    Acesso: DIRETOR, COLABORADOR.
    """
    template_name = 'escola/escola_dash.html'
    tipo_permitido = [UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.request.escola
        context['ano_corrente'] = escola.ano_letivo_corrente
        # context['salas'] será adicionado quando apps.sala for reativado
        return context


# ---------------------------------------------------------------------------
# Edição da escola
# ---------------------------------------------------------------------------

class EditarEscola(PermissaoRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Edição dos dados cadastrais da escola.
    Acesso: ADMIN, DIRETOR.
    """
    model = UnidadeEscolar
    form_class = EscolaForm
    template_name = 'escola/editar_escola.html'
    success_message = 'Dados da escola atualizados com sucesso.'
    success_url = reverse_lazy('escola:dash_escola')
    context_object_name = 'escola'
    permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR]

    def get_object(self, queryset=None):
        return get_object_or_404(UnidadeEscolar, pk=self.request.escola.pk)


class EditarEndereco(PermissaoRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Edição do endereço da escola.
    Cria o endereço automaticamente se ainda não existir.
    Acesso: ADMIN, DIRETOR.
    """
    model = EnderecoEscolar
    form_class = EnderecoEscolarForm
    template_name = 'escola/editar_endereco.html'
    success_message = 'Endereço atualizado com sucesso.'
    success_url = reverse_lazy('escola:dash_escola')
    context_object_name = 'endereco'
    permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR]

    def get_object(self, queryset=None):
        endereco, _ = EnderecoEscolar.objects.get_or_create(
            escola=self.request.escola,
            defaults={
                'rua': '', 'numero': '', 'bairro': '',
                'cep': '', 'cidade': '', 'estado': '',
            },
        )
        return endereco


# ---------------------------------------------------------------------------
# Views comentadas — dependem de apps desativados temporariamente
# ---------------------------------------------------------------------------

# from apps.sala.models import Sala
# from apps.aluno.models import Aluno
# from apps.frequencia.models import Frequencia

# class UnidAlunos(PermissaoRequiredMixin, ListView):
#     model = Aluno
#     template_name = 'escola/adm_unidade_alunos.html'
#     context_object_name = 'alunos'
#     permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]
#
#     def get_queryset(self):
#         return Aluno.objects.filter(sala_id=self.kwargs['id']).order_by('nome')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['escola'] = self.request.escola
#         context['sala'] = get_object_or_404(Sala, id=self.kwargs['id'])
#         return context

# class FrequenciaRelatorios(PermissaoRequiredMixin, TemplateView):
#     template_name = 'escola/relatorio_frequencia.html'
#     permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['sala'] = get_object_or_404(Sala, pk=self.kwargs['pk'])
#         return context


# ---------------------------------------------------------------------------
# API — mobile
# ---------------------------------------------------------------------------

class MinhaEscolaView(APIView):
    """
    Retorna as escolas vinculadas ao usuário autenticado via JWT.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vinculos = (
            UsuarioEscola.objects
            .filter(usuario=request.user, ativo=True)
            .select_related('escola')
        )
        escolas = [v.escola for v in vinculos]
        return Response(UnidadeEscolarSerializer(escolas, many=True).data)


class EscolaDetalheUpdateView(RetrieveUpdateAPIView):
    """
    Recupera ou atualiza dados de uma escola específica.
    O usuário precisa ter vínculo ativo (ADMIN ou DIRETOR) com a escola.
    """
    serializer_class = UnidadeEscolarSerializerEdit
    permission_classes = [IsAuthenticated]

    def get_object(self):
        escola_id = self.kwargs.get('pk')
        vinculo = (
            UsuarioEscola.objects
            .filter(
                usuario=self.request.user,
                escola_id=escola_id,
                ativo=True,
                tipo_usuario__in=[UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR],
            )
            .select_related('escola')
            .first()
        )
        if not vinculo:
            raise PermissionDenied
        return vinculo.escola


class EnderecoEscolarUpdateView(RetrieveUpdateAPIView):
    """
    Recupera ou atualiza o endereço de uma escola.
    O usuário precisa ter vínculo ativo (ADMIN ou DIRETOR) com a escola.
    """
    serializer_class = EnderecoEscolarSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        escola_id = self.kwargs.get('pk')
        vinculo = (
            UsuarioEscola.objects
            .filter(
                usuario=self.request.user,
                escola_id=escola_id,
                ativo=True,
                tipo_usuario__in=[UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR],
            )
            .select_related('escola')
            .first()
        )
        if not vinculo:
            raise PermissionDenied
        endereco, _ = EnderecoEscolar.objects.get_or_create(
            escola=vinculo.escola,
            defaults={
                'rua': '', 'numero': '', 'bairro': '',
                'cep': '', 'cidade': '', 'estado': '',
            },
        )
        return endereco
