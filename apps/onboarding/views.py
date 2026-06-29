from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, View

from apps.escola.models import UnidadeEscolar

from .forms import CompletarCadastroForm, CriarEscolaForm
from .services import onboarding_service


class PlatformAdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_platform_admin:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Super Admin — gestão de escolas e convites
# ---------------------------------------------------------------------------

class ListarEscolasView(PlatformAdminRequiredMixin, TemplateView):
    template_name = 'onboarding/lista_escolas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escolas = (
            UnidadeEscolar.objects
            .select_related('assinatura')
            .prefetch_related('convites')
            .order_by('nome')
        )
        context['escolas'] = escolas
        context['usuario'] = self.request.user
        return context


class CriarEscolaView(PlatformAdminRequiredMixin, View):
    template_name = 'onboarding/form_criar_escola.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': CriarEscolaForm(),
            'usuario': request.user,
        })

    def post(self, request):
        form = CriarEscolaForm(request.POST)
        if form.is_valid():
            try:
                escola, convite = onboarding_service.criar_escola_e_convite(
                    dados_escola={
                        'nome':  form.cleaned_data['nome_escola'],
                        'cnpj':  form.cleaned_data.get('cnpj', ''),
                        'tipo':  form.cleaned_data['tipo'],
                    },
                    dados_diretor={
                        'nome':     form.cleaned_data['nome_diretor'],
                        'email':    form.cleaned_data['email_diretor'],
                        'telefone': form.cleaned_data.get('telefone_diretor', ''),
                    },
                    canal_envio=form.cleaned_data['canal_envio'],
                    criado_por=request.user,
                )
                messages.success(
                    request,
                    f'Escola "{escola.nome}" criada. Convite enviado para {convite.email}.',
                )
                return redirect('onboarding:listar_escolas')
            except Exception as exc:
                messages.error(request, f'Erro ao criar escola: {exc}')
        return render(request, self.template_name, {'form': form, 'usuario': request.user})


class ReenviarConviteView(PlatformAdminRequiredMixin, View):
    def post(self, request, pk):
        escola     = get_object_or_404(UnidadeEscolar, pk=pk)
        canal      = request.POST.get('canal_envio', 'EMAIL')
        try:
            onboarding_service.reenviar_convite(escola, canal, request.user)
            messages.success(request, 'Convite reenviado com sucesso.')
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect('onboarding:listar_escolas')


# ---------------------------------------------------------------------------
# Diretor — completar cadastro via convite
# ---------------------------------------------------------------------------

class CompletarOnboardingView(View):
    template_name = 'onboarding/completar_cadastro.html'

    def _get_convite_ou_redirecionar(self, token):
        try:
            return onboarding_service.validar_token(str(token)), None
        except ValueError:
            return None, redirect('onboarding:link_invalido')

    def get(self, request, token):
        convite, redir = self._get_convite_ou_redirecionar(token)
        if redir:
            return redir
        return render(request, self.template_name, {
            'form': CompletarCadastroForm(),
            'convite': convite,
        })

    def post(self, request, token):
        convite, redir = self._get_convite_ou_redirecionar(token)
        if redir:
            return redir
        form = CompletarCadastroForm(request.POST)
        if form.is_valid():
            try:
                onboarding_service.completar_onboarding(
                    token=str(token),
                    senha=form.cleaned_data['senha'],
                    dados_perfil={
                        'cpf':             form.cleaned_data.get('cpf', ''),
                        'data_nascimento': form.cleaned_data.get('data_nascimento'),
                        'cargo':           form.cleaned_data['cargo'],
                        'telefone':        form.cleaned_data.get('telefone', ''),
                        'data_inicio':     form.cleaned_data.get('data_inicio'),
                    },
                )
                messages.success(
                    request,
                    'Cadastro concluído! Faça login com seu e-mail e senha para acessar o sistema.',
                )
                return redirect('accounts:login')
            except ValueError as exc:
                messages.error(request, str(exc))
        return render(request, self.template_name, {'form': form, 'convite': convite})


class LinkInvalidoView(TemplateView):
    template_name = 'onboarding/link_invalido.html'
