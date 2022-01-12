from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import UserCreationDirecao
from .models import DirecaoEscolar
from ..escola.models import UnidadeEscolar


class CadDirecao(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = DirecaoEscolar
    form_class = UserCreationDirecao
    template_name = 'direcao/direcao_form.html'
    success_message = 'Membro da direção escolar cadastrado com sucesso.'
    success_url = reverse_lazy('direcao:lista_direcao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        funcionario = form.save(commit=False)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        funcionario.escola = escola
        funcionario.is_funcionario = True
        funcionario.save()
        return super().form_valid(form)


class DirecaoLista(LoginRequiredMixin, ListView):
    model = DirecaoEscolar
    template_name = 'direcao/lista_form.html'

    def get_queryset(self):
        return DirecaoEscolar.objects.filter(escola=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context

