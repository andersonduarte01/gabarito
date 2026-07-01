from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views import View

from .forms import AcademicaForm, FrequenciaForm, ProfessorForm
from .services import configuracao_service


class DiretorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo != 'DIRETOR':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel}


class ConfiguracaoAcademicaView(DiretorRequiredMixin, View):
    template_name = 'configuracao/academica.html'

    def get(self, request):
        form = AcademicaForm(instance=configuracao_service.obter_academica(request.escola))
        return render(request, self.template_name, {**self._ctx(request), 'form': form})

    def post(self, request):
        form = AcademicaForm(request.POST, instance=configuracao_service.obter_academica(request.escola))
        if form.is_valid():
            configuracao_service.atualizar_academica(request.escola, form.cleaned_data)
            messages.success(request, 'Configurações acadêmicas salvas.')
            return redirect('configuracao:academica')
        return render(request, self.template_name, {**self._ctx(request), 'form': form})


class ConfiguracaoFrequenciaView(DiretorRequiredMixin, View):
    template_name = 'configuracao/frequencia.html'

    def get(self, request):
        form = FrequenciaForm(instance=configuracao_service.obter_frequencia(request.escola))
        return render(request, self.template_name, {**self._ctx(request), 'form': form})

    def post(self, request):
        form = FrequenciaForm(request.POST, instance=configuracao_service.obter_frequencia(request.escola))
        if form.is_valid():
            configuracao_service.atualizar_frequencia(request.escola, form.cleaned_data)
            messages.success(request, 'Configurações de frequência salvas.')
            return redirect('configuracao:frequencia')
        return render(request, self.template_name, {**self._ctx(request), 'form': form})


class ConfiguracaoProfessorView(DiretorRequiredMixin, View):
    template_name = 'configuracao/professor.html'

    def get(self, request):
        form = ProfessorForm(instance=configuracao_service.obter_professor(request.escola))
        return render(request, self.template_name, {**self._ctx(request), 'form': form})

    def post(self, request):
        form = ProfessorForm(request.POST, instance=configuracao_service.obter_professor(request.escola))
        if form.is_valid():
            configuracao_service.atualizar_professor(request.escola, form.cleaned_data)
            messages.success(request, 'Configurações de professor salvas.')
            return redirect('configuracao:professor')
        return render(request, self.template_name, {**self._ctx(request), 'form': form})
