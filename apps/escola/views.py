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

    def _dados_perfil(self, request):
        from apps.ano_letivo.models import AnoLetivo, StatusAnoLetivo
        escola    = request.escola
        enderecos = escola.enderecos.all().order_by('-principal', 'id')
        segmentos = escola.segmentos.all().order_by('tipo')
        tipos_usados = list(segmentos.values_list('tipo', flat=True))
        todos_tipos  = {v for v, _ in TipoSegmento.choices}
        tem_disponivel = bool(todos_tipos - set(tipos_usados))
        ano_ativo = (
            AnoLetivo.objects
            .filter(escola=escola, status=StatusAnoLetivo.EM_ANDAMENTO)
            .first()
        )
        anos_total = AnoLetivo.objects.filter(escola=escola).count()
        segmentos_com_series = [
            {'segmento': seg, 'total': seg.series.filter(ativo=True).count()}
            for seg in segmentos
        ]
        from apps.materia.models import Materia
        total_materias = Materia.objects.filter(escola=escola, ativo=True).count()
        return (
            escola, enderecos, segmentos, tipos_usados, tem_disponivel,
            ano_ativo, anos_total, segmentos_com_series, total_materias,
        )

    def get(self, request):
        escola, enderecos, segmentos, tipos_usados, tem_disponivel, ano_ativo, anos_total, segmentos_com_series, total_materias = self._dados_perfil(request)
        form_segmento = AdicionarSegmentoForm(existentes=tipos_usados)
        return render(request, self.template_name, self._ctx(
            request,
            enderecos=enderecos,
            segmentos=segmentos,
            form_segmento=form_segmento,
            tem_disponivel=tem_disponivel,
            ano_ativo=ano_ativo,
            anos_total=anos_total,
            segmentos_com_series=segmentos_com_series,
            total_materias=total_materias,
        ))

    def post(self, request):
        escola, enderecos, segmentos, tipos_usados, tem_disponivel, ano_ativo, anos_total, segmentos_com_series, total_materias = self._dados_perfil(request)
        form_segmento = AdicionarSegmentoForm(request.POST, existentes=tipos_usados)
        if form_segmento.is_valid():
            tipo = form_segmento.cleaned_data['tipo']
            if tipo and tipo not in tipos_usados:
                adicionar_segmento(escola, tipo)
                messages.success(request, 'Segmento adicionado.')
            return redirect('escola:perfil')
        return render(request, self.template_name, self._ctx(
            request,
            enderecos=enderecos,
            segmentos=segmentos,
            form_segmento=form_segmento,
            tem_disponivel=tem_disponivel,
            ano_ativo=ano_ativo,
            anos_total=anos_total,
            segmentos_com_series=segmentos_com_series,
            total_materias=total_materias,
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
        return redirect('escola:perfil')
