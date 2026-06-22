from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView, RedirectView, View

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from apps.core.views import BaseDashboardView
from apps.aluno.models import Aluno
from apps.sala.models import Turma, Serie
from .forms import EscolaForm, EnderecoEscolarForm, AnoLetivoForm, SerieForm
from .models import UnidadeEscolar, EnderecoEscolar, AnoLetivo
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

class DashEscola(BaseDashboardView):
    """Painel principal da escola — acessível a todos os vínculos ativos."""
    template_name = 'escola/escola_dash.html'
    tipo_permitido = [
        UsuarioEscola.DIRETOR,
        UsuarioEscola.COLABORADOR,
        UsuarioEscola.PROFESSOR,
        UsuarioEscola.ALUNO,
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.request.escola
        ano = escola.ano_letivo_corrente
        context['ano_corrente'] = ano

        salas_qs = (
            Turma.objects
            .filter(escola=escola)
            .select_related('ano_letivo')
            .annotate(num_alunos=Count('alunos'))
            .order_by('nome')
        )
        if ano:
            salas_qs = salas_qs.filter(ano_letivo=ano)

        context['salas'] = salas_qs
        context['total_salas'] = salas_qs.count()
        context['total_alunos'] = (
            Aluno.objects.filter(escola=escola, situacao='MATRIC').count()
        )
        context['total_colaboradores'] = (
            UsuarioEscola.objects
            .filter(escola=escola, tipo_usuario=UsuarioEscola.COLABORADOR, ativo=True)
            .count()
        )
        return context


# ---------------------------------------------------------------------------
# Perfil da escola
# ---------------------------------------------------------------------------

class PerfilEscola(PermissaoRequiredMixin, TemplateView):
    """Página de perfil completo da escola — leitura + links de edição."""
    template_name = 'escola/perfil_escola.html'
    permissao_tipos = [UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        escola = self.request.escola
        ctx['escola'] = escola
        ctx['ano_corrente'] = escola.ano_letivo_corrente
        ctx['anos_letivos'] = escola.anos_letivos.order_by('-ano')
        try:
            ctx['endereco'] = escola.endereco_obj
        except Exception:
            ctx['endereco'] = None
        try:
            ctx['diretor'] = escola.diretor
        except Exception:
            ctx['diretor'] = None
        ctx['series_perfil'] = Serie.objects.filter(escola=escola).order_by('ordem', 'nome')
        return ctx


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
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def get_object(self, queryset=None):
        return get_object_or_404(UnidadeEscolar, pk=self.request.escola.pk)


class EditarEndereco(PermissaoRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Edição do endereço da escola.
    Cria o endereço automaticamente se ainda não existir.
    """
    model = EnderecoEscolar
    form_class = EnderecoEscolarForm
    template_name = 'escola/editar_endereco.html'
    success_message = 'Endereço atualizado com sucesso.'
    success_url = reverse_lazy('escola:dash_escola')
    context_object_name = 'endereco'
    permissao_tipos = [UsuarioEscola.DIRETOR]

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
# Anos Letivos
# ---------------------------------------------------------------------------

class ListaAnosLetivos(PermissaoRequiredMixin, TemplateView):
    template_name    = 'escola/ano_letivo_lista.html'
    permissao_tipos  = [UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['anos'] = (
            self.request.escola.anos_letivos
            .annotate(total_salas=Count('turmas'))
            .order_by('-ano')
        )
        ctx['ano_corrente'] = self.request.escola.ano_letivo_corrente
        return ctx


class AdicionarAnoLetivo(PermissaoRequiredMixin, SuccessMessageMixin, CreateView):
    model            = AnoLetivo
    form_class       = AnoLetivoForm
    template_name    = 'escola/ano_letivo_form.html'
    success_url      = reverse_lazy('escola:anos_letivos')
    success_message  = 'Ano letivo %(ano)s criado com sucesso.'
    permissao_tipos  = [UsuarioEscola.DIRETOR]

    def form_valid(self, form):
        form.instance.escola = self.request.escola
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modo'] = 'criar'
        return ctx


class EditarAnoLetivo(PermissaoRequiredMixin, SuccessMessageMixin, UpdateView):
    model            = AnoLetivo
    form_class       = AnoLetivoForm
    template_name    = 'escola/ano_letivo_form.html'
    success_url      = reverse_lazy('escola:anos_letivos')
    success_message  = 'Ano letivo %(ano)s atualizado com sucesso.'
    permissao_tipos  = [UsuarioEscola.DIRETOR]

    def get_queryset(self):
        return AnoLetivo.objects.filter(escola=self.request.escola)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modo'] = 'editar'
        return ctx


class DefinirAnoCorrente(PermissaoRequiredMixin, View):
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def post(self, request, pk):
        ano_letivo = get_object_or_404(AnoLetivo, pk=pk, escola=request.escola)
        ano_letivo.corrente = True
        ano_letivo.save()
        messages.success(request, f'Ano letivo {ano_letivo.ano} definido como corrente.')
        return redirect('escola:anos_letivos')


class RemoverAnoLetivo(PermissaoRequiredMixin, DeleteView):
    model           = AnoLetivo
    template_name   = 'escola/ano_letivo_confirmar_remocao.html'
    success_url     = reverse_lazy('escola:anos_letivos')
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def get_queryset(self):
        return AnoLetivo.objects.filter(escola=self.request.escola)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_salas'] = self.object.turmas.count()
        return ctx

    def form_valid(self, form):
        ano = self.object.ano
        response = super().form_valid(form)
        messages.success(self.request, f'Ano letivo {ano} removido com sucesso.')
        return response


# ---------------------------------------------------------------------------
# Séries
# ---------------------------------------------------------------------------

class ListaSeries(PermissaoRequiredMixin, TemplateView):
    template_name   = 'escola/serie_lista.html'
    permissao_tipos = [UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['series'] = (
            Serie.objects
            .filter(escola=self.request.escola)
            .annotate(total_turmas=Count('turmas'))
            .order_by('ordem', 'nome')
        )
        return ctx


class AdicionarSerie(PermissaoRequiredMixin, SuccessMessageMixin, CreateView):
    model           = Serie
    form_class      = SerieForm
    template_name   = 'escola/serie_form.html'
    success_url     = reverse_lazy('escola:series')
    success_message = 'Série "%(nome)s" criada com sucesso.'
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def form_valid(self, form):
        form.instance.escola = self.request.escola
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modo'] = 'criar'
        return ctx


class EditarSerie(PermissaoRequiredMixin, SuccessMessageMixin, UpdateView):
    model           = Serie
    form_class      = SerieForm
    template_name   = 'escola/serie_form.html'
    success_url     = reverse_lazy('escola:series')
    success_message = 'Série "%(nome)s" atualizada com sucesso.'
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def get_queryset(self):
        return Serie.objects.filter(escola=self.request.escola)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modo'] = 'editar'
        return ctx


class RemoverSerie(PermissaoRequiredMixin, DeleteView):
    model           = Serie
    success_url     = reverse_lazy('escola:series')
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def get_queryset(self):
        return Serie.objects.filter(escola=self.request.escola)

    def get(self, request, *args, **kwargs):
        return redirect('escola:series')

    def form_valid(self, form):
        nome     = self.object.nome
        response = super().form_valid(form)
        messages.success(self.request, f'Série "{nome}" removida com sucesso.')
        return response


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
                tipo_usuario__in=[UsuarioEscola.DIRETOR],
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
    O usuário precisa ter vínculo ativo (DIRETOR) com a escola.
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
                tipo_usuario__in=[UsuarioEscola.DIRETOR],
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
