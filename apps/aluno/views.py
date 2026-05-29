from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, TemplateView, UpdateView
from django.urls import reverse_lazy

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from apps.core.services import AlunoService
from .forms import AlunoCreateForm, AlunoEditForm
from .models import Aluno


_TIPOS_GESTAO = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]


class ListaAlunos(PermissaoRequiredMixin, ListView):
    model = Aluno
    template_name = 'aluno/lista_alunos.html'
    context_object_name = 'alunos'
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        qs = (
            Aluno.objects
            .filter(escola=self.request.escola)
            .select_related('usuario', 'sala', 'sala__ano')
            .order_by('usuario__nome')
        )
        sala_id = self.request.GET.get('sala')
        if sala_id:
            qs = qs.filter(sala_id=sala_id)
        return qs

    def get_context_data(self, **kwargs):
        from apps.sala.models import Sala
        ctx = super().get_context_data(**kwargs)
        ctx['salas'] = Sala.objects.filter(escola=self.request.escola).order_by('descricao')
        ctx['sala_selecionada'] = self.request.GET.get('sala', '')
        return ctx


class CadastrarAluno(PermissaoRequiredMixin, TemplateView):
    template_name = 'aluno/form_aluno.html'
    permissao_tipos = _TIPOS_GESTAO

    def get_context_data(self, form=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = form or AlunoCreateForm(escola=self.request.escola)
        ctx['titulo'] = 'Cadastrar Aluno'
        return ctx

    def post(self, request, *args, **kwargs):
        form = AlunoCreateForm(request.POST, escola=request.escola)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        d = form.cleaned_data
        service = AlunoService(request.escola)
        result = service.criar_aluno(
            nome=d['nome'],
            cpf=d.get('cpf') or '',
            data_nascimento=d.get('data_nascimento'),
            sala=d.get('sala'),
            tem_responsavel=d.get('tem_responsavel', True),
            email=d.get('email'),
            password=d.get('password'),
            sexo=d.get('sexo', 'M'),
        )

        if result['status'] == 'error':
            messages.error(request, result['message'])
            return self.render_to_response(self.get_context_data(form=form))

        if result['status'] == 'exists':
            messages.warning(request, result['message'])
        else:
            messages.success(request, 'Aluno cadastrado com sucesso.')

        aluno = result.get('aluno')
        if aluno and d.get('responsavel_legal'):
            aluno.responsavel_legal = d['responsavel_legal']
            aluno.save(update_fields=['responsavel_legal'])

        return redirect('aluno:lista_alunos')


class EditarAluno(PermissaoRequiredMixin, UpdateView):
    model = Aluno
    form_class = AlunoEditForm
    template_name = 'aluno/form_aluno.html'
    context_object_name = 'aluno'
    permissao_tipos = _TIPOS_GESTAO
    success_url = reverse_lazy('aluno:lista_alunos')

    def get_object(self, queryset=None):
        return get_object_or_404(Aluno, pk=self.kwargs['pk'], escola=self.request.escola)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['escola'] = self.request.escola
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar — {self.object.usuario.nome}'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Aluno atualizado com sucesso.')
        return super().form_valid(form)


class DesativarAluno(PermissaoRequiredMixin, TemplateView):
    template_name = 'aluno/confirmar_remocao.html'
    permissao_tipos = _TIPOS_GESTAO

    def get_object(self):
        return get_object_or_404(Aluno, pk=self.kwargs['pk'], escola=self.request.escola)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['objeto'] = self.get_object()
        return ctx

    def post(self, request, *args, **kwargs):
        aluno = self.get_object()
        aluno.usuario.remover_escola(request.escola)
        messages.success(request, f'{aluno.usuario.nome} foi desativado.')
        return redirect('aluno:lista_alunos')
