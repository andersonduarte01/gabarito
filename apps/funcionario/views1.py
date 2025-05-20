from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView

from .forms import UserCreationFuncionario, DesignarFuncaoForm, UserCreationProfessor
from .models import Funcionario, Professor
from ..aluno.models import Aluno
from ..core.models import Usuario
from ..escola.models import UnidadeEscolar, AnoLetivo
from ..funcao.models import Funcao
from ..perfil.models import Endereco, Pessoa
from ..sala.models import Sala


class DashFuncionario(LoginRequiredMixin, TemplateView):
    template_name = 'funcionario/funcionario_dash.html'


class DashProfessor(LoginRequiredMixin, TemplateView):
    template_name = 'funcionario/professor_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = get_object_or_404(Professor, pk=self.request.user)
        escola = get_object_or_404(UnidadeEscolar, pk=professor.escola.pk)
        ano_corrente = AnoLetivo.objects.get(corrente=True)
        salas = Sala.objects.filter(escola=escola, ano_letivo=ano_corrente).order_by('ano')
        context['escola'] = escola
        context['salas'] = salas
        context['data'] = now()
        return context


class CadastrarFuncionario(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Funcionario
    form_class = UserCreationFuncionario
    template_name = 'funcionario/adicionar_funcionario.html'
    success_message = 'Membro da direção escolar cadastrado com sucesso.'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

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


class EditarFuncionario(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Usuario
    fields = ('email', 'nome')
    success_message = 'Informações do usuário atualizadas.'
    template_name = 'funcionario/editar_funcionario.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class ListaFuncionarios(LoginRequiredMixin, ListView):
    model = Funcionario
    template_name = 'funcionario/lista_funcionarios.html'

    def get_queryset(self):
        return Funcionario.objects.filter(escola=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class EnderecoEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Endereco
    fields = '__all__'
    success_message = 'Endereço atualizado com sucesso'
    template_name = 'funcionario/editar_endereco.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_object(self, queryset=None):
        funcionario = Funcionario.objects.get(pk=self.kwargs['pk'])
        return Endereco.objects.get(pk=funcionario.endereco.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class EnderecoAdicionar(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Endereco
    fields = '__all__'
    success_message = 'Endereço adicionado com sucesso'
    template_name = 'funcionario/adicionar_endereco.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def form_valid(self, form):
        endereco = form.save()
        funcionario = Funcionario.objects.get(pk=self.kwargs['pk'])
        funcionario.endereco = endereco
        funcionario.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class PerfilAdicionar(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Pessoa
    fields = '__all__'
    success_message = 'Perfil adicionado com sucesso'
    template_name = 'funcionario/adicionar_perfil.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def form_valid(self, form):
        perfil = form.save()
        funcionario = Funcionario.objects.get(pk=self.kwargs['pk'])
        funcionario.perfil = perfil
        funcionario.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class EditarPerfil(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Pessoa
    fields = '__all__'
    success_message = 'Perfil atualizado com sucesso'
    template_name = 'funcionario/editar_perfil.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_object(self, queryset=None):
        funcionario = Funcionario.objects.get(pk=self.kwargs['pk'])
        return Pessoa.objects.get(pk=funcionario.perfil.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        return context


class DesignarFuncao(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Funcionario
    form_class = DesignarFuncaoForm
    success_message = 'Função designada com sucesso'
    template_name = 'funcionario/designar_funcao.html'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_object(self, queryset=None):
        return Funcionario.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        context['funcionario'] = Funcionario.objects.get(pk=self.kwargs['pk'])
        funcao = Funcao.objects.filter(escola=self.request.user)
        context['funcao'] = funcao
        return context


class DeletarDirecao(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Funcionario
    success_message = 'Funcionário removido com sucesso!'
    success_url = reverse_lazy('funcionario:lista_funcionarios')

    def get_object(self, queryset=None):
        return Funcionario.objects.get(pk=self.kwargs['pk'])


#################################### Professor ######################


class UniCadastrarProfessor(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Professor
    form_class = UserCreationProfessor
    template_name = 'funcionario/adicionar_professor.html'
    success_message = 'Cadastro Realizado com sucesso!'
    success_url = reverse_lazy('funcionario:lista_professores')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        context['escola'] = escola
        return context

    def form_valid(self, form):
        professor = form.save(commit=False)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        professor.escola = escola
        professor.is_professor = True
        professor.save()
        return super().form_valid(form)


class UniListaProfessores(LoginRequiredMixin, ListView):
    model = Professor
    template_name = 'funcionario/lista_professores.html'

    def get_queryset(self):
        return Professor.objects.filter(escola=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        context['escola'] = escola
        return context


class UniEditarProfessor(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Professor
    fields = ('email', 'professor_nome')
    success_message = 'Informações do professor atualizadas.'
    template_name = 'funcionario/editar_professor.html'
    success_url = reverse_lazy('funcionario:lista_professores')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        context['escola'] = escola
        context['professor'] = get_object_or_404(Professor, pk=self.kwargs['pk'])
        return context


class UniDeletarProfessor(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Professor
    success_message = 'Professor removido com sucesso!'
    success_url = reverse_lazy('funcionario:lista_professores')

    def get_object(self, queryset=None):
        return Professor.objects.get(pk=self.kwargs['pk'])


class ListaProf(LoginRequiredMixin, ListView):
    model = Professor
    template_name = 'funcionario/lista_prof.html'

    def get_queryset(self):
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        return Professor.objects.filter(escola=escola)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        context['escola'] = escola
        context['professor'] = professor
        return context


class ProUnidAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'funcionario/prof_unidade_alunos.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        return Aluno.objects.filter(sala_id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = get_object_or_404(Professor, pk=self.request.user)
        escola = get_object_or_404(UnidadeEscolar, pk=professor.escola.id)
        sala = get_object_or_404(Sala, id=self.kwargs['id'])
        context['escola'] = escola
        context['sala'] = sala
        return context

