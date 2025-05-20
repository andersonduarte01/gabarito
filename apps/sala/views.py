import datetime

from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import ExtractMonth
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import SalaForm, EditarSalaForm
from ..aluno.models import Aluno
from ..avaliacao.models import Avaliacao
from ..escola.models import UnidadeEscolar, AnoLetivo
from ..frequencia.models import Registro
from ..funcionario.models import Professor
from ..sala.models import Sala


class AdicionarSala(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = SalaForm
    model = Sala
    template_name = 'sala/adicionar_sala.html'
    success_message = 'Sala cadastrada com sucesso.'
    success_url = reverse_lazy('escola:dash_escola')

    def get_escola(self):
        return get_object_or_404(UnidadeEscolar, pk=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.get_escola()
        context['escola'] = escola
        return context

    def form_valid(self, form):
        sala = form.save(commit=False)
        sala.escola = self.get_escola()
        sala.save()
        return super().form_valid(form)


class EditarSala(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = EditarSalaForm
    model = Sala
    success_message = 'Sala atualizada com sucesso.'
    template_name = 'sala/editar_sala.html'

    def get_success_url(self):
        return reverse('escola:dash_escola')


class DeletarSala(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Sala
    success_message = 'Sala removida com sucesso!'

    def get_object(self, queryset=None):
        return Sala.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('escola:dash_escola')