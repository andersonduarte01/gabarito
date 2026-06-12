from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views.generic import TemplateView, UpdateView, ListView, RedirectView, CreateView, FormView, View
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import EscolaContextMixin, ApenasAdminMixin, SuperAdminMixin

from .forms import (
    FiltroMesForm, EscolaForm, EnderecoForm1, UsuarioForm,
    CadastrarUsuarioForm, CriarEscolaForm, CriarAdminEscolaForm,
)
from .models import UnidadeEscolar, EnderecoEscolar, AnoLetivo, UsuarioEscola
from .serializers import UnidadeEscolarSerializer, EnderecoEscolarSerializer, UnidadeEscolarSerializerEdit
from ..aluno.models import Aluno
from ..core.models import Usuario
from ..sala.models import Sala


# ── Seleção de escola (pós-login, pré-dashboard) ───────────────────────────

class SelecionarEscola(LoginRequiredMixin, TemplateView):
    """
    Exibida quando o usuário tem vínculo em mais de uma escola.
    Armazena escola_id na sessão e redireciona para o dashboard correto.
    """
    template_name = 'escola/selecionar_escola.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        vinculos = self._vinculos(request)

        # Sem vínculo algum → logout
        if not vinculos.exists():
            logout(request)
            return redirect('login')

        # Única escola → auto-seleciona e vai direto
        if vinculos.count() == 1:
            vinculo = vinculos.first()
            request.session['escola_id'] = vinculo.escola_id
            return redirect(request.user.get_dashboard_url(vinculo.escola))

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        escola_id = request.POST.get('escola_id')
        vinculos = self._vinculos(request)

        try:
            vinculo = vinculos.get(escola_id=escola_id)
        except UsuarioEscola.DoesNotExist:
            return self.get(request, *args, **kwargs)

        request.session['escola_id'] = vinculo.escola_id
        return redirect(request.user.get_dashboard_url(vinculo.escola))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vinculos'] = self._vinculos(self.request)
        return context

    @staticmethod
    def _vinculos(request):
        return (
            UsuarioEscola.objects
            .filter(usuario=request.user, ativo=True)
            .select_related('escola')
            .order_by('escola__nome_escola')
        )


# ── Redirecionamento após login ────────────────────────────────────────────

class Redireciona(LoginRequiredMixin, RedirectView):
    """Ponto de entrada após login: seleciona escola ou vai ao dashboard."""

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        escola_id = self.request.session.get('escola_id')

        # Super admin sem escola selecionada → painel admin global
        if user.is_admin and not escola_id:
            return reverse('escola:painel_adm')

        # Escola já na sessão → dashboard direto
        if escola_id:
            try:
                escola = UnidadeEscolar.objects.get(id=escola_id)
                return user.get_dashboard_url(escola)
            except UnidadeEscolar.DoesNotExist:
                self.request.session.pop('escola_id', None)

        vinculos = UsuarioEscola.objects.filter(usuario=user, ativo=True).select_related('escola')

        if not vinculos.exists():
            # Usuário sem vínculo → logout
            logout(self.request)
            return reverse('login')

        if vinculos.count() == 1:
            vinculo = vinculos.first()
            self.request.session['escola_id'] = vinculo.escola_id
            return user.get_dashboard_url(vinculo.escola)

        return reverse('escola:selecionar_escola')


# ── Dashboards ─────────────────────────────────────────────────────────────

class DashAdmin(EscolaContextMixin, TemplateView):
    """Dashboard do administrador: lista escolas do usuário (ou todas se superadmin)."""
    template_name = 'escola/administrador_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_admin:
            escolas = UnidadeEscolar.objects.filter(ativa=True)
        else:
            escolas = UnidadeEscolar.objects.filter(
                vinculos__usuario=user,
                vinculos__tipo=UsuarioEscola.ADMINISTRADOR,
                vinculos__ativo=True,
                ativa=True,
            )

        context['escolas'] = escolas
        return context


class DashEscola(EscolaContextMixin, TemplateView):
    """Dashboard da escola — usa request.escola injetado pelo middleware."""
    template_name = 'escola/escola_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.request.escola

        try:
            ano_corrente = AnoLetivo.objects.get(corrente=True)
        except AnoLetivo.DoesNotExist:
            ano_corrente = None

        salas = Sala.objects.filter(escola=escola, ano_letivo=ano_corrente).order_by('ano') if ano_corrente else []

        context['escola'] = escola
        context['salas'] = salas
        context['data'] = now()
        context['ano_letivo'] = ano_corrente
        return context


# ── Edições ────────────────────────────────────────────────────────────────

class EditarEscola(EscolaContextMixin, SuccessMessageMixin, UpdateView):
    form_class = EscolaForm
    model = UnidadeEscolar
    success_message = 'Informações atualizadas com sucesso!'
    template_name = 'escola/editarescolar_form.html'
    success_url = reverse_lazy('escola:painel_escola')
    context_object_name = 'escola'

    def get_object(self, queryset=None):
        return get_object_or_404(UnidadeEscolar, pk=self.kwargs['pk'])


class EditarEndereco(EscolaContextMixin, SuccessMessageMixin, UpdateView):
    form_class = EnderecoForm1
    model = EnderecoEscolar
    template_name = 'escola/editarendereco_form.html'
    context_object_name = 'escola'
    success_message = 'Endereço atualizado com sucesso!'
    success_url = reverse_lazy('escola:painel_escola')

    def get_object(self, queryset=None):
        return get_object_or_404(EnderecoEscolar, escola=self.request.escola)


class EditarUsuario(EscolaContextMixin, SuccessMessageMixin, UpdateView):
    form_class = UsuarioForm
    model = Usuario
    success_message = 'Informações atualizadas com sucesso!'
    template_name = 'escola/editarusuario_form.html'
    success_url = reverse_lazy('escola:painel_escola')


# ── Alunos ─────────────────────────────────────────────────────────────────

class UnidAlunos(EscolaContextMixin, ListView):
    model = Aluno
    template_name = 'escola/adm_unidade_alunos.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        return Aluno.objects.filter(sala_id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escola'] = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        context['sala'] = get_object_or_404(Sala, id=self.kwargs['id'])
        return context


class ListAlunos(EscolaContextMixin, CreateView):
    model = Aluno
    fields = ('nome', 'data_nascimento', 'sexo')
    template_name = 'escola/lista_alunos.html'
    context_object_name = 'alunos'

    def form_valid(self, form):
        aluno = form.save(commit=False)
        sala = Sala.objects.get(id=self.kwargs['id'])
        sala.total_alunos += 1
        sala.save()
        aluno.sala = sala
        aluno.save()
        return super().form_valid(form)

    def get_success_url(self):
        ctx = self.get_context_data()
        return reverse('escola:unidade_sala_alunos', kwargs={
            'id': ctx['sala'].id,
            'slug': ctx['escola'].slug,
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['id'])
        context['sala'] = sala
        context['alunos'] = Aluno.objects.filter(sala=sala).order_by('nome')
        context['escola'] = self.request.escola or UnidadeEscolar.objects.get(pk=sala.escola.pk)
        return context


class FrequenciaRelatorios(EscolaContextMixin, TemplateView):
    template_name = 'escola/relatorio_frequencia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escola'] = self.request.escola
        context['sala'] = get_object_or_404(Sala, pk=self.kwargs['pk'])
        return context


# ── Gestão de usuários da escola ───────────────────────────────────────────

class GerenciarUsuarios(ApenasAdminMixin, FormView):
    """Lista os usuários da escola e permite cadastrar professores/funcionários/alunos."""
    template_name = 'escola/gerenciar_usuarios.html'
    form_class = CadastrarUsuarioForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Administrador só pode ser criado pelo superadmin
        form.fields['tipo'].choices = [
            (k, v) for k, v in UsuarioEscola.TIPOS
            if k != UsuarioEscola.ADMINISTRADOR
        ]
        return form

    def get_success_url(self):
        return reverse('escola:gerenciar_usuarios')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['vinculos'] = (
            UsuarioEscola.objects
            .filter(escola=self.request.escola)
            .select_related('usuario')
            .order_by('tipo', 'usuario__nome')
        )
        return ctx

    def form_valid(self, form):
        data = form.cleaned_data
        with transaction.atomic():
            user = Usuario.objects.create_user(
                email=data['email'],
                nome=data['nome'],
                password=data['senha'],
            )
            UsuarioEscola.objects.create(
                usuario=user,
                escola=self.request.escola,
                tipo=data['tipo'],
            )
        messages.success(self.request, f'Usuário {data["nome"]} cadastrado com sucesso!')
        return super().form_valid(form)


class ToggleUsuarioAtivo(ApenasAdminMixin, View):
    """Ativa ou desativa o vínculo de um usuário com a escola."""
    def post(self, request, pk):
        vinculo = get_object_or_404(UsuarioEscola, pk=pk, escola=request.escola)

        if vinculo.usuario == request.user:
            messages.error(request, 'Você não pode alterar seu próprio vínculo.')
            return redirect('escola:gerenciar_usuarios')

        vinculo.ativo = not vinculo.ativo
        vinculo.save(update_fields=['ativo', 'data_atualizacao'])
        acao = 'ativado' if vinculo.ativo else 'desativado'
        messages.success(request, f'{vinculo.usuario.nome} foi {acao}.')
        return redirect('escola:gerenciar_usuarios')


class RemoverVinculo(ApenasAdminMixin, View):
    """Remove o vínculo do usuário com a escola (não exclui a conta)."""
    def post(self, request, pk):
        vinculo = get_object_or_404(UsuarioEscola, pk=pk, escola=request.escola)

        if vinculo.usuario == request.user:
            messages.error(request, 'Você não pode remover seu próprio vínculo.')
            return redirect('escola:gerenciar_usuarios')

        nome = vinculo.usuario.nome
        vinculo.delete()
        messages.success(request, f'Vínculo de {nome} removido com sucesso.')
        return redirect('escola:gerenciar_usuarios')


# ── Superadmin: cadastrar escola e administrador ───────────────────────────

class SuperadminCadastros(SuperAdminMixin, TemplateView):
    """
    Painel exclusivo do superadmin para criar escolas e seus administradores.
    Trata dois formulários independentes na mesma página via campo `acao`.
    """
    template_name = 'escola/superadmin_cadastros.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault('form_escola', CriarEscolaForm(prefix='escola'))
        ctx.setdefault('form_admin', CriarAdminEscolaForm(prefix='admin'))
        ctx['escolas'] = (
            UnidadeEscolar.objects
            .filter(ativa=True)
            .prefetch_related('vinculos__usuario')
            .order_by('nome_escola')
        )
        return ctx

    def post(self, request, *args, **kwargs):
        acao = request.POST.get('acao')

        if acao == 'escola':
            form = CriarEscolaForm(request.POST, prefix='escola')
            if form.is_valid():
                escola = form.save()
                messages.success(request, f'Escola "{escola.nome_escola}" cadastrada com sucesso.')
                return redirect('escola:superadmin_cadastros')
            ctx = self.get_context_data()
            ctx['form_escola'] = form
            return self.render_to_response(ctx)

        if acao == 'admin':
            form = CriarAdminEscolaForm(request.POST, prefix='admin')
            if form.is_valid():
                data = form.cleaned_data
                with transaction.atomic():
                    user = Usuario.objects.create_user(
                        email=data['email'],
                        nome=data['nome'],
                        password=data['senha'],
                    )
                    UsuarioEscola.objects.create(
                        usuario=user,
                        escola=data['escola'],
                        tipo=UsuarioEscola.ADMINISTRADOR,
                    )
                messages.success(
                    request,
                    f'Administrador {data["nome"]} cadastrado e vinculado a {data["escola"]}.'
                )
                return redirect('escola:superadmin_cadastros')
            ctx = self.get_context_data()
            ctx['form_admin'] = form
            return self.render_to_response(ctx)

        return redirect('escola:superadmin_cadastros')


# ── API ────────────────────────────────────────────────────────────────────

class EscolaLogadaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        escola_id = request.session.get('escola_id')
        if not escola_id:
            return Response({'erro': 'Nenhuma escola selecionada.'}, status=403)
        try:
            escola = UnidadeEscolar.objects.get(id=escola_id)
        except UnidadeEscolar.DoesNotExist:
            return Response({'erro': 'Escola não encontrada.'}, status=404)
        return Response(UnidadeEscolarSerializer(escola).data)


class UnidadeEscolarUpdateView(RetrieveUpdateAPIView):
    serializer_class = UnidadeEscolarSerializerEdit
    permission_classes = [IsAuthenticated]

    def get_object(self):
        escola_id = self.request.session.get('escola_id')
        return get_object_or_404(UnidadeEscolar, id=escola_id)


class EnderecoEscolarUpdateView(RetrieveUpdateAPIView):
    serializer_class = EnderecoEscolarSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        escola_id = self.request.session.get('escola_id')
        return get_object_or_404(EnderecoEscolar, escola_id=escola_id)
