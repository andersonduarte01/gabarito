from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from apps.core.services import AlunoService
from apps.sala.models import Turma
from .forms import AlunoCreateForm, AlunoEditForm
from .models import Aluno, SITUACAO


_TIPOS_GESTAO = [UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]


class ListaAlunos(PermissaoRequiredMixin, TemplateView):
    template_name = 'aluno/lista_alunos.html'
    permissao_tipos = _TIPOS_GESTAO

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        escola = self.request.escola

        qs = (
            Aluno.objects
            .filter(escola=escola)
            .select_related('usuario', 'sala')
            .order_by('usuario__nome')
        )

        turma_id = self.request.GET.get('turma', '')
        situacao  = self.request.GET.get('situacao', '')

        if turma_id:
            qs = qs.filter(sala_id=turma_id)
        if situacao:
            qs = qs.filter(situacao=situacao)

        alunos = list(qs)
        ctx['alunos']           = alunos
        ctx['total']            = len(alunos)
        ctx['turmas']           = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
        ctx['situacao_choices'] = SITUACAO
        ctx['filtros']          = {'turma': turma_id, 'situacao': situacao}
        return ctx


class CadastrarAluno(PermissaoRequiredMixin, TemplateView):
    template_name = 'aluno/form_aluno.html'
    permissao_tipos = _TIPOS_GESTAO

    def get_context_data(self, form=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = form or AlunoCreateForm(escola=self.request.escola)
        ctx['modo'] = 'criar'
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
            email=d.get('email') or None,
            password=d.get('password') or None,
            sexo=d.get('sexo') or '',
            matricula=d.get('matricula') or '',
            telefone=d.get('telefone') or '',
            responsavel_legal=d.get('responsavel_legal') or '',
            telefone_responsavel=d.get('telefone_responsavel') or '',
        )

        if result['status'] == 'error':
            messages.error(request, result['message'])
            return self.render_to_response(self.get_context_data(form=form))

        if result['status'] == 'exists':
            messages.warning(request, result['message'])
        else:
            messages.success(request, f'Aluno {d["nome"]} cadastrado com sucesso.')

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
        ctx['modo'] = 'editar'
        return ctx

    def form_valid(self, form):
        usuario = self.object.usuario
        usuario.nome = form.cleaned_data['nome']
        novo_email = (form.cleaned_data.get('email') or '').strip()
        if novo_email and novo_email != usuario.email:
            usuario.email = novo_email
        usuario.save(update_fields=['nome', 'email'])
        messages.success(self.request, f'Aluno {usuario.nome} atualizado com sucesso.')
        return super().form_valid(form)


class DesativarAluno(PermissaoRequiredMixin, TemplateView):
    permissao_tipos = [UsuarioEscola.DIRETOR]

    def get(self, request, *args, **kwargs):
        return redirect('aluno:lista_alunos')

    def post(self, request, *args, **kwargs):
        aluno = get_object_or_404(Aluno, pk=self.kwargs['pk'], escola=request.escola)
        nome = aluno.usuario.nome
        aluno.usuario.remover_escola(request.escola)
        messages.success(request, f'{nome} foi desativado.')
        return redirect('aluno:lista_alunos')
