from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.escola.models import EnderecoEscolar, SegmentoEscolar, TipoSegmento

from .forms import AdicionarSegmentoForm, EnderecoEscolarForm, EscolaForm
from .services.escola_service import (
    adicionar_segmento,
    definir_endereco_principal,
    remover_endereco,
    remover_segmento,
)


class EscolaRequiredMixin:
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


class PerfilEscolaView(EscolaRequiredMixin, View):
    template_name = 'escola/perfil_escola.html'

    def get(self, request):
        enderecos = request.escola.enderecos.all().order_by('-principal', 'id')
        return render(request, self.template_name, self._ctx(request, enderecos=enderecos))


class SegmentosView(EscolaRequiredMixin, View):
    template_name = 'escola/segmentos.html'

    def _dados(self, request):
        escola = request.escola
        segmentos = escola.segmentos.all().order_by('tipo')
        tipos_usados = list(segmentos.values_list('tipo', flat=True))
        tem_disponivel = bool({v for v, _ in TipoSegmento.choices} - set(tipos_usados))
        return escola, segmentos, tipos_usados, tem_disponivel

    def get(self, request):
        escola, segmentos, tipos_usados, tem_disponivel = self._dados(request)
        form = AdicionarSegmentoForm(existentes=tipos_usados)
        return render(request, self.template_name, self._ctx(
            request, segmentos=segmentos, form=form, tem_disponivel=tem_disponivel,
        ))

    def post(self, request):
        escola, segmentos, tipos_usados, tem_disponivel = self._dados(request)
        form = AdicionarSegmentoForm(request.POST, existentes=tipos_usados)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            if tipo and tipo not in tipos_usados:
                adicionar_segmento(escola, tipo)
                messages.success(request, 'Segmento adicionado.')
            return redirect('escola:segmentos')
        return render(request, self.template_name, self._ctx(
            request, segmentos=segmentos, form=form, tem_disponivel=tem_disponivel,
        ))


class EditarEscolaView(EscolaRequiredMixin, View):
    template_name = 'escola/editar_escola.html'

    def get(self, request):
        form = EscolaForm(instance=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form))

    def post(self, request):
        form = EscolaForm(request.POST, request.FILES, instance=request.escola)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados da escola atualizados.')
            return redirect('escola:perfil')
        return render(request, self.template_name, self._ctx(request, form=form))


class AdicionarEnderecoView(EscolaRequiredMixin, View):
    template_name = 'escola/form_endereco.html'

    def get(self, request):
        form = EnderecoEscolarForm()
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))

    def post(self, request):
        form = EnderecoEscolarForm(request.POST)
        if form.is_valid():
            endereco = form.save(commit=False)
            endereco.escola = request.escola
            endereco.save()
            messages.success(request, 'Endereço adicionado.')
            return redirect('escola:perfil')
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))


class EditarEnderecoView(EscolaRequiredMixin, View):
    template_name = 'escola/form_endereco.html'

    def _get_endereco(self, request, pk):
        return get_object_or_404(EnderecoEscolar, pk=pk, escola=request.escola)

    def get(self, request, pk):
        endereco = self._get_endereco(request, pk)
        form = EnderecoEscolarForm(instance=endereco)
        return render(request, self.template_name,
                      self._ctx(request, form=form, editando=True, endereco=endereco))

    def post(self, request, pk):
        endereco = self._get_endereco(request, pk)
        form = EnderecoEscolarForm(request.POST, instance=endereco)
        if form.is_valid():
            form.save()
            if endereco.principal:
                definir_endereco_principal(endereco)
            messages.success(request, 'Endereço atualizado.')
            return redirect('escola:perfil')
        return render(request, self.template_name,
                      self._ctx(request, form=form, editando=True, endereco=endereco))


class DefinirPrincipalView(EscolaRequiredMixin, View):
    def post(self, request, pk):
        endereco = get_object_or_404(EnderecoEscolar, pk=pk, escola=request.escola)
        definir_endereco_principal(endereco)
        messages.success(request, 'Endereço principal definido.')
        return redirect('escola:perfil')


class RemoverEnderecoView(EscolaRequiredMixin, View):
    def post(self, request, pk):
        endereco = get_object_or_404(EnderecoEscolar, pk=pk, escola=request.escola)
        remover_endereco(endereco)
        messages.success(request, 'Endereço removido.')
        return redirect('escola:perfil')


class RemoverSegmentoView(EscolaRequiredMixin, View):
    def post(self, request, pk):
        segmento = get_object_or_404(SegmentoEscolar, pk=pk, escola=request.escola)
        remover_segmento(segmento)
        messages.success(request, 'Segmento removido.')
        return redirect('escola:segmentos')
