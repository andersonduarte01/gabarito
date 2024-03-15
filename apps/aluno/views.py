from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, ListView, CreateView, TemplateView, UpdateView

from ..aluno.models import Aluno
from ..avaliacao.models import Gabarito, Resposta
from .forms import AlunoForm, EditarAlunoForm, PessoaForm, EnderecoForm, EditarAlunoForm01
from ..escola.models import UnidadeEscolar
from ..perfil.models import Pessoa, Endereco
from ..sala.models import Sala


class AddAluno(LoginRequiredMixin, CreateView):
    form_class = AlunoForm
    template_name = 'aluno/adicionar_aluno.html'
    success_url = reverse_lazy('escola:painel_escola')

    def get_form_kwargs(self):
        kwargs = super(AddAluno, self).get_form_kwargs()
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        kwargs['escola'] = escola
        return kwargs


def editar_aluno(request, pk):
    perfil = ''
    endereco = ''
    aluno = get_object_or_404(Aluno, pk=pk)
    escola = UnidadeEscolar.objects.get(pk=aluno.sala.escola.id)
    try:
        perfil = Pessoa.objects.get(pk=aluno.perfil.id)
        endereco = Endereco.objects.get(pk=aluno.endereco.id)
    except:
        print('Vazio')

    if request.method == 'POST':
        form = EditarAlunoForm(request.POST, instance=aluno)
        form1 = PessoaForm(request.POST, instance=perfil)
        form2 = EnderecoForm(request.POST, instance=endereco)
        if form.is_valid and form1.is_valid() and form2.is_valid():
            aluno = form.save(commit=False)
            perfil = form1.save()
            endereco = form2.save()
            aluno.perfil = perfil
            aluno.endereco = endereco
            aluno.save()
            url = reverse('salas:alunos', kwargs={'pk': aluno.sala.pk})
            return HttpResponseRedirect(url)

    else:
        form = EditarAlunoForm(instance=aluno)
        form1 = PessoaForm(instance=perfil)
        form2 = EnderecoForm(instance=endereco)

    context = {'form': form, 'form1': form1, 'form2': form2, 'escola': escola, 'aluno': aluno, }
    return render(request, "aluno/editar_aluno.html", context)


class EditarAluno(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Aluno
    form_class = EditarAlunoForm01
    template_name = 'aluno/edicao_aluno.html'
    success_message = 'Aluno atualizado com sucesso.'

    def get_success_url(self):
        print(self.object.sala.pk)
        return reverse_lazy('salas:alunos', kwargs={'pk': self.object.sala.pk})

class DeletarAluno(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Aluno
    success_message = 'Aluno removido com sucesso!'

    def get_object(self, queryset=None):
        return Aluno.objects.get(pk=self.kwargs['pk'])


def delete_view(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    sala = get_object_or_404(Sala, id=aluno.sala.id)
    if request.method == "POST":
        aluno.delete()
        sala.total_alunos -= 1
        sala.save()
        url = reverse('salas:alunos', kwargs={'pk': aluno.sala.pk})
        return HttpResponseRedirect(url)

    url = reverse('salas:alunos', kwargs={'pk': aluno.sala.pk})
    return HttpResponseRedirect(url)


class ProvasView(ListView):
    model = Gabarito
    template_name = 'aluno/mostrar.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        return Gabarito.objects.filter(aluno=self.kwargs['pk'])


class ProvaView(ListView):
    model = Resposta
    template_name = 'aluno/prova.html'
    context_object_name = 'respostas'

    def get_queryset(self):
        gabarito = Gabarito.objects.get(pk=self.kwargs['pk'])
        return Resposta.objects.filter(gabarito=gabarito)


class ResultadoPesquisa(ListView):
    model = Aluno
    template_name = 'aluno/resultado.html'

    def get_queryset(self):
        salas = Sala.objects.filter(escola=self.request.user)
        query = self.request.GET.get("q")
        object_list = Aluno.objects.filter(Q(nome__icontains=query), sala__in=salas)
        return object_list


class Pesquisar(TemplateView):
    template_name = 'aluno/pesquisar.html'


class PerfilAluno(ListView):
    model = Aluno
    template_name = 'aluno/perfil_aluno.html'
    context_object_name = 'aluno'

    def get_queryset(self):
        return Aluno.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = Aluno.objects.get(pk=self.kwargs['pk'])
        return context

