from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from apps.core.services import UsuarioService
from .forms import ColaboradorCreateForm, ColaboradorEditForm, ProfessorCreateForm, ProfessorEditForm
from .models import Colaborador, Professor


_TIPOS_GESTAO = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]


# ---------------------------------------------------------------------------
# Colaboradores
# ---------------------------------------------------------------------------

class ListaColaboradores(PermissaoRequiredMixin, ListView):
    model = Colaborador
    template_name = 'colaborador/lista_colaboradores.html'
    context_object_name = 'colaboradores'
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        return (
            Colaborador.objects
            .filter(escola=self.request.escola, ativo=True)
            .select_related('usuario', 'funcao')
            .order_by('usuario__nome')
        )


class CadastrarColaborador(PermissaoRequiredMixin, TemplateView):
    template_name = 'colaborador/form_colaborador.html'
    permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = ColaboradorCreateForm(escola=self.request.escola)
        ctx['titulo'] = 'Cadastrar Colaborador'
        return ctx

    def post(self, request, *args, **kwargs):
        form = ColaboradorCreateForm(request.POST, request.FILES, escola=request.escola)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        d = form.cleaned_data
        service = UsuarioService(request.escola)
        result = service.processar_usuario(
            email=d['email'],
            nome=d['nome'],
            tipo_usuario=UsuarioEscola.COLABORADOR,
            password=d['password'],
            cpf=d.get('cpf') or None,
            perfil_model=Colaborador,
            perfil_data={
                'escola': request.escola,
                'funcao': d.get('funcao'),
                'cpf': d.get('cpf', ''),
                'telefone': d.get('telefone', ''),
            },
        )

        if result['status'] == 'error':
            messages.error(request, result['message'])
            return self.render_to_response(self.get_context_data(form=form))

        if result['status'] == 'exists':
            messages.warning(request, result['message'])
        else:
            messages.success(request, 'Colaborador cadastrado com sucesso.')

        if result.get('perfil') and d.get('foto'):
            perfil = result['perfil']
            perfil.foto = d['foto']
            perfil.save(update_fields=['foto'])

        return redirect('colaborador:lista_colaboradores')

    def get_context_data(self, form=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = form or ColaboradorCreateForm(escola=self.request.escola)
        ctx['titulo'] = 'Cadastrar Colaborador'
        return ctx


class EditarColaborador(PermissaoRequiredMixin, TemplateView):
    template_name = 'colaborador/form_colaborador.html'
    permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR]

    def get_object(self):
        return get_object_or_404(
            Colaborador, pk=self.kwargs['pk'], escola=self.request.escola
        )

    def get_context_data(self, form=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.get_object()
        ctx['form'] = form or ColaboradorEditForm(instance=obj, escola=self.request.escola)
        ctx['titulo'] = f'Editar — {obj.usuario.nome}'
        ctx['objeto'] = obj
        return ctx

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        form = ColaboradorEditForm(
            request.POST, request.FILES, instance=obj, escola=request.escola
        )
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        d = form.cleaned_data
        usuario = obj.usuario
        usuario.nome = d['nome']
        usuario.email = d['email']
        usuario.save(update_fields=['nome', 'email'])

        obj.cpf = d.get('cpf', '')
        obj.telefone = d.get('telefone', '')
        obj.funcao = d.get('funcao')
        if d.get('foto'):
            obj.foto = d['foto']
        obj.save()

        messages.success(request, 'Colaborador atualizado com sucesso.')
        return redirect('colaborador:lista_colaboradores')


class DesativarColaborador(PermissaoRequiredMixin, TemplateView):
    template_name = 'colaborador/confirmar_remocao.html'
    permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR]

    def get_object(self):
        return get_object_or_404(
            Colaborador, pk=self.kwargs['pk'], escola=self.request.escola
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['objeto'] = self.get_object()
        ctx['tipo'] = 'colaborador'
        return ctx

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.ativo = False
        obj.save(update_fields=['ativo'])
        obj.usuario.remover_escola(request.escola)
        messages.success(request, f'{obj.usuario.nome} foi desativado.')
        return redirect('colaborador:lista_colaboradores')


# ---------------------------------------------------------------------------
# Professores
# ---------------------------------------------------------------------------

class ListaProfessores(PermissaoRequiredMixin, ListView):
    model = Professor
    template_name = 'colaborador/lista_professores.html'
    context_object_name = 'professores'
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        return (
            Professor.objects
            .filter(escola=self.request.escola, ativo=True)
            .select_related('usuario')
            .order_by('usuario__nome')
        )


class CadastrarProfessor(PermissaoRequiredMixin, TemplateView):
    template_name = 'colaborador/form_professor.html'
    permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR]

    def get_context_data(self, form=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = form or ProfessorCreateForm()
        ctx['titulo'] = 'Cadastrar Professor'
        return ctx

    def post(self, request, *args, **kwargs):
        form = ProfessorCreateForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        d = form.cleaned_data
        service = UsuarioService(request.escola)
        result = service.processar_usuario(
            email=d['email'],
            nome=d['nome'],
            tipo_usuario=UsuarioEscola.PROFESSOR,
            password=d['password'],
            cpf=d.get('cpf') or None,
            perfil_model=Professor,
            perfil_data={
                'escola': request.escola,
                'cpf': d.get('cpf', ''),
                'telefone': d.get('telefone', ''),
            },
        )

        if result['status'] == 'error':
            messages.error(request, result['message'])
            return self.render_to_response(self.get_context_data(form=form))

        if result['status'] == 'exists':
            messages.warning(request, result['message'])
        else:
            messages.success(request, 'Professor cadastrado com sucesso.')

        if result.get('perfil') and d.get('foto'):
            result['perfil'].foto = d['foto']
            result['perfil'].save(update_fields=['foto'])

        return redirect('colaborador:lista_professores')


class EditarProfessor(PermissaoRequiredMixin, TemplateView):
    template_name = 'colaborador/form_professor.html'
    permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR]

    def get_object(self):
        return get_object_or_404(
            Professor, pk=self.kwargs['pk'], escola=self.request.escola
        )

    def get_context_data(self, form=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.get_object()
        ctx['form'] = form or ProfessorEditForm(instance=obj)
        ctx['titulo'] = f'Editar — {obj.usuario.nome}'
        ctx['objeto'] = obj
        return ctx

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        form = ProfessorEditForm(request.POST, request.FILES, instance=obj)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        d = form.cleaned_data
        obj.usuario.nome = d['nome']
        obj.usuario.email = d['email']
        obj.usuario.save(update_fields=['nome', 'email'])

        obj.cpf = d.get('cpf', '')
        obj.telefone = d.get('telefone', '')
        if d.get('foto'):
            obj.foto = d['foto']
        obj.save()

        messages.success(request, 'Professor atualizado com sucesso.')
        return redirect('colaborador:lista_professores')


class DesativarProfessor(PermissaoRequiredMixin, TemplateView):
    template_name = 'colaborador/confirmar_remocao.html'
    permissao_tipos = [UsuarioEscola.ADMIN, UsuarioEscola.DIRETOR]

    def get_object(self):
        return get_object_or_404(
            Professor, pk=self.kwargs['pk'], escola=self.request.escola
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['objeto'] = self.get_object()
        ctx['tipo'] = 'professor'
        return ctx

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.ativo = False
        obj.save(update_fields=['ativo'])
        obj.usuario.remover_escola(request.escola)
        messages.success(request, f'{obj.usuario.nome} foi desativado.')
        return redirect('colaborador:lista_professores')
