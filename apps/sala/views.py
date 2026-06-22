from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from apps.aluno.models import Aluno
from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from apps.escola.models import AnoLetivo
from .forms import TurmaForm
from .models import Serie, Turma, TURNO_CHOICES

_TIPOS_GESTAO = [UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]


# ── Turmas ────────────────────────────────────────────────────────────────────

class ListaTurmas(PermissaoRequiredMixin, TemplateView):
    template_name  = 'sala/lista_turmas.html'
    permissao_tipos = _TIPOS_GESTAO

    def get_context_data(self, **kwargs):
        ctx    = super().get_context_data(**kwargs)
        escola = self.request.escola

        qs = (
            Turma.objects
            .filter(escola=escola)
            .select_related('ano_letivo', 'serie')
            .annotate(alunos_count=Count('alunos'))
            .order_by('nome')
        )

        serie         = self.request.GET.get('serie', '')
        turno         = self.request.GET.get('turno', '')
        ano_letivo_id = self.request.GET.get('ano_letivo', '')
        ativo         = self.request.GET.get('ativo', '')

        if serie:
            qs = qs.filter(serie_id=serie)
        if turno:
            qs = qs.filter(turno=turno)
        if ano_letivo_id:
            qs = qs.filter(ano_letivo_id=ano_letivo_id)
        if ativo == '1':
            qs = qs.filter(ativo=True)
        elif ativo == '0':
            qs = qs.filter(ativo=False)

        turmas               = list(qs)
        ctx['turmas']        = turmas
        ctx['total']         = len(turmas)
        ctx['series']        = Serie.objects.filter(escola=escola).order_by('ordem', 'nome')
        ctx['anos_letivos']  = AnoLetivo.objects.filter(escola=escola).order_by('-ano')
        ctx['turno_choices'] = TURNO_CHOICES
        ctx['filtros'] = {
            'serie':      serie,
            'turno':      turno,
            'ano_letivo': ano_letivo_id,
            'ativo':      ativo,
        }
        return ctx


class DetalhesTurma(PermissaoRequiredMixin, TemplateView):
    template_name   = 'sala/detalhe_turma.html'
    permissao_tipos = _TIPOS_GESTAO

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        turma = get_object_or_404(
            Turma.objects.annotate(alunos_count=Count('alunos')),
            pk=self.kwargs['pk'],
            escola=self.request.escola,
        )
        ctx['turma']  = turma
        ctx['alunos'] = (
            Aluno.objects
            .filter(sala=turma)
            .select_related('usuario')
            .order_by('usuario__nome')
        )
        return ctx


class AdicionarTurma(PermissaoRequiredMixin, SuccessMessageMixin, CreateView):
    model           = Turma
    form_class      = TurmaForm
    template_name   = 'sala/form_turma.html'
    success_message = 'Turma %(nome)s criada com sucesso.'
    success_url     = reverse_lazy('turma:lista_turmas')
    permissao_tipos = _TIPOS_GESTAO

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['escola'] = self.request.escola
        kwargs['modo']   = 'criar'
        return kwargs

    def form_valid(self, form):
        form.instance.escola = self.request.escola
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modo'] = 'criar'
        return ctx


class EditarTurma(PermissaoRequiredMixin, SuccessMessageMixin, UpdateView):
    model           = Turma
    form_class      = TurmaForm
    template_name   = 'sala/form_turma.html'
    success_message = 'Turma %(nome)s atualizada com sucesso.'
    success_url     = reverse_lazy('turma:lista_turmas')
    permissao_tipos = _TIPOS_GESTAO

    def get_object(self, queryset=None):
        return get_object_or_404(Turma, pk=self.kwargs['pk'], escola=self.request.escola)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['escola'] = self.request.escola
        kwargs['modo']   = 'editar'
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['modo'] = 'editar'
        return ctx


class RemoverTurma(PermissaoRequiredMixin, DeleteView):
    model           = Turma
    success_url     = reverse_lazy('turma:lista_turmas')
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def get_object(self, queryset=None):
        return get_object_or_404(Turma, pk=self.kwargs['pk'], escola=self.request.escola)

    def get(self, request, *args, **kwargs):
        return redirect('turma:lista_turmas')

    def form_valid(self, form):
        nome     = self.object.nome
        response = super().form_valid(form)
        messages.success(self.request, f'Turma {nome} removida com sucesso.')
        return response

