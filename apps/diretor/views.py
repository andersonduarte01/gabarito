from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from .forms import DiretorForm
from .models import Diretor


def _get_or_create_diretor(request):
    diretor, _ = Diretor.objects.get_or_create(
        usuario=request.user,
        escola=request.escola,
        defaults={'ativo': True},
    )
    return diretor


class MeuPerfil(PermissaoRequiredMixin, TemplateView):
    """Perfil do diretor — visualização com link para edição."""
    template_name = 'diretor/meu_perfil.html'
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['diretor'] = _get_or_create_diretor(self.request)
        return ctx


class EditarPerfil(PermissaoRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edição dos dados pessoais do diretor."""
    model = Diretor
    form_class = DiretorForm
    template_name = 'diretor/editar_perfil.html'
    success_message = 'Perfil atualizado com sucesso.'
    success_url = reverse_lazy('diretor:meu_perfil')
    context_object_name = 'diretor'
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def get_object(self, queryset=None):
        return _get_or_create_diretor(self.request)
