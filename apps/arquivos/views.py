from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, UpdateView

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from .forms import ArquivoForm, CategoriaArquivoForm, LivroForm, VideoForm
from .models import Arquivo, CategoriaArquivo, Livro, Video, SERIE_CHOICES

_TIPOS_GESTAO = [UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]
_TIPOS_ACESSO = [
    UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR,
    UsuarioEscola.PROFESSOR, UsuarioEscola.ALUNO,
]

_MAPA_ANOS = {
    '1Ano': '1º Ano', '2Ano': '2º Ano', '3Ano': '3º Ano',
    '4Ano': '4º Ano', '5Ano': '5º Ano', '6Ano': '6º Ano',
    '7Ano': '7º Ano', '8Ano': '8º Ano', '9Ano': '9º Ano',
}


def _qs_arquivos_publicos(request):
    escola = getattr(request, 'escola', None)
    qs = Arquivo.publicos.select_related('autor', 'escola')
    if escola:
        return qs.filter(
            Q(visibilidade=Arquivo.PUBLICA)
            | Q(visibilidade=Arquivo.PRIVADA, escola=escola)
        )
    return qs.filter(visibilidade=Arquivo.PUBLICA)


def _qs_livros_publicos(request):
    escola = getattr(request, 'escola', None)
    qs = Livro.objects.select_related('categoria', 'escola')
    if escola:
        return qs.filter(
            Q(visibilidade=Livro.PUBLICA)
            | Q(visibilidade=Livro.PRIVADA, escola=escola)
        )
    return qs.filter(visibilidade=Livro.PUBLICA)


# ---------------------------------------------------------------------------
# Arquivo — público
# ---------------------------------------------------------------------------

class ArquivoLista(ListView):
    model = Arquivo
    template_name = 'arquivos/arquivos.html'
    context_object_name = 'arquivos'
    paginate_by = 12

    def get_queryset(self):
        return _qs_arquivos_publicos(self.request).order_by('-criado_em')


class PesquisarArquivo(ListView):
    model = Arquivo
    template_name = 'arquivos/arquivos_resultado.html'
    context_object_name = 'arquivos'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Arquivo.objects.none()
        return (
            _qs_arquivos_publicos(self.request)
            .filter(Q(titulo__icontains=query) | Q(descricao__icontains=query))
            .order_by('-criado_em')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


# ---------------------------------------------------------------------------
# Arquivo — gestão (autenticado + permissão)
# ---------------------------------------------------------------------------

class ArquivoAdd(PermissaoRequiredMixin, CreateView):
    model = Arquivo
    form_class = ArquivoForm
    template_name = 'arquivos/arquivo.html'
    success_url = reverse_lazy('arquivos:lista_arquivos')
    permissao_tipos = _TIPOS_GESTAO

    def form_valid(self, form):
        form.instance.autor = self.request.user
        form.instance.escola = self.request.escola
        messages.success(self.request, 'Arquivo adicionado com sucesso.')
        return super().form_valid(form)


class ArquivoEditar(PermissaoRequiredMixin, UpdateView):
    model = Arquivo
    form_class = ArquivoForm
    template_name = 'arquivos/arquivo_up.html'
    success_url = reverse_lazy('arquivos:lista_arquivos')
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        return Arquivo.objects.filter(escola=self.request.escola)

    def form_valid(self, form):
        messages.success(self.request, 'Arquivo atualizado.')
        return super().form_valid(form)


class DeletarArquivo(PermissaoRequiredMixin, DeleteView):
    model = Arquivo
    success_url = reverse_lazy('arquivos:lista_arquivos')
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        return Arquivo.objects.filter(escola=self.request.escola)

    def form_valid(self, form):
        messages.success(self.request, 'Arquivo removido.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Categoria — gestão
# ---------------------------------------------------------------------------

class CategoriaList(PermissaoRequiredMixin, ListView):
    model = CategoriaArquivo
    template_name = 'arquivos/lista_categoria.html'
    context_object_name = 'categorias'
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        return CategoriaArquivo.objects.all()


class CategoriaAdd(PermissaoRequiredMixin, CreateView):
    model = CategoriaArquivo
    form_class = CategoriaArquivoForm
    template_name = 'arquivos/categoria.html'
    success_url = reverse_lazy('arquivos:lista_categoria')
    permissao_tipos = _TIPOS_GESTAO

    def form_valid(self, form):
        messages.success(self.request, 'Categoria adicionada com sucesso.')
        return super().form_valid(form)


class CategoriaEditar(PermissaoRequiredMixin, UpdateView):
    model = CategoriaArquivo
    form_class = CategoriaArquivoForm
    template_name = 'arquivos/categoria_up.html'
    success_url = reverse_lazy('arquivos:lista_categoria')
    permissao_tipos = _TIPOS_GESTAO

    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada.')
        return super().form_valid(form)


class DeletarCategoria(PermissaoRequiredMixin, DeleteView):
    model = CategoriaArquivo
    success_url = reverse_lazy('arquivos:lista_categoria')
    permissao_tipos = _TIPOS_GESTAO

    def form_valid(self, form):
        messages.success(self.request, 'Categoria removida.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Biblioteca / Livros — público
# ---------------------------------------------------------------------------

class BibliotecaLista(ListView):
    model = Livro
    template_name = 'arquivos/biblioteca_novo.html'
    context_object_name = 'livros'
    paginate_by = 16

    def get_queryset(self):
        qs = _qs_livros_publicos(self.request)
        categoria_slug = self.request.GET.get('categoria', '').strip()
        if categoria_slug:
            qs = qs.filter(categoria__slug=categoria_slug)
        return qs.order_by('titulo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaArquivo.objects.all()
        context['categoria_ativa'] = self.request.GET.get('categoria', '')
        return context


class PesquisarLivro(ListView):
    model = Livro
    template_name = 'arquivos/biblioteca_resultado.html'
    context_object_name = 'livros'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Livro.objects.none()
        return (
            _qs_livros_publicos(self.request)
            .filter(Q(titulo__icontains=query) | Q(autor__icontains=query))
            .order_by('titulo')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


# ---------------------------------------------------------------------------
# Biblioteca — gestão
# ---------------------------------------------------------------------------

class LivroAdd(PermissaoRequiredMixin, CreateView):
    model = Livro
    form_class = LivroForm
    template_name = 'arquivos/livro.html'
    success_url = reverse_lazy('arquivos:lista_livros')
    permissao_tipos = _TIPOS_GESTAO

    def form_valid(self, form):
        form.instance.escola = self.request.escola
        messages.success(self.request, 'Livro adicionado com sucesso.')
        return super().form_valid(form)


class LivroEditar(PermissaoRequiredMixin, UpdateView):
    model = Livro
    form_class = LivroForm
    template_name = 'arquivos/livro_up.html'
    success_url = reverse_lazy('arquivos:lista_livros')
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        return Livro.objects.filter(escola=self.request.escola)

    def form_valid(self, form):
        messages.success(self.request, 'Livro atualizado.')
        return super().form_valid(form)


class DeletarLivro(PermissaoRequiredMixin, DeleteView):
    model = Livro
    success_url = reverse_lazy('arquivos:lista_livros')
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        return Livro.objects.filter(escola=self.request.escola)

    def form_valid(self, form):
        messages.success(self.request, 'Livro removido.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Vídeos / Tutoriais — acesso autenticado
# ---------------------------------------------------------------------------

class TutoriaisLista(PermissaoRequiredMixin, ListView):
    model = Video
    template_name = 'arquivos/tutoriais.html'
    context_object_name = 'videos'
    paginate_by = 20
    permissao_tipos = _TIPOS_ACESSO

    def get_queryset(self):
        qs = Video.objects.order_by('numero', 'titulo')
        ano_slug = self.request.GET.get('ano', '').strip()
        materia = self.request.GET.get('materia', '').strip()
        if ano_slug:
            qs = qs.filter(ano=_MAPA_ANOS.get(ano_slug, ano_slug))
        if materia:
            qs = qs.filter(sigla__iexact=materia)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['serie_choices'] = SERIE_CHOICES
        context['materias'] = (
            Video.objects.values_list('sigla', 'materia')
            .distinct().order_by('materia')
        )
        return context


class AnoMateria(PermissaoRequiredMixin, ListView):
    model = Video
    template_name = 'arquivos/tutoriais00.html'
    context_object_name = 'videos'
    permissao_tipos = _TIPOS_ACESSO

    def get_queryset(self):
        descricao = _MAPA_ANOS.get(self.kwargs['ano'], self.kwargs['ano'])
        return Video.objects.filter(ano=descricao, sigla=self.kwargs['sigla']).order_by('numero')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sigla'] = self.kwargs.get('sigla', '')
        context['ano_param'] = self.kwargs.get('ano', '')
        return context


class PesquisarVideo(PermissaoRequiredMixin, ListView):
    model = Video
    template_name = 'arquivos/tutoriais_resultado.html'
    context_object_name = 'videos'
    paginate_by = 20
    permissao_tipos = _TIPOS_ACESSO

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Video.objects.none()
        return (
            Video.objects
            .filter(Q(titulo__icontains=query) | Q(materia__icontains=query))
            .select_related('ano')
            .order_by('numero')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


# ---------------------------------------------------------------------------
# Vídeos — gestão
# ---------------------------------------------------------------------------

class VideoAdd(PermissaoRequiredMixin, CreateView):
    model = Video
    form_class = VideoForm
    template_name = 'arquivos/video_form.html'
    success_url = reverse_lazy('arquivos:lista_tutoriais')
    permissao_tipos = _TIPOS_GESTAO

    def form_valid(self, form):
        messages.success(self.request, 'Vídeo adicionado com sucesso.')
        return super().form_valid(form)


class VideoEditar(PermissaoRequiredMixin, UpdateView):
    model = Video
    form_class = VideoForm
    template_name = 'arquivos/video_form.html'
    success_url = reverse_lazy('arquivos:lista_tutoriais')
    permissao_tipos = _TIPOS_GESTAO

    def form_valid(self, form):
        messages.success(self.request, 'Vídeo atualizado.')
        return super().form_valid(form)


class DeletarVideo(PermissaoRequiredMixin, DeleteView):
    model = Video
    success_url = reverse_lazy('arquivos:lista_tutoriais')
    permissao_tipos = _TIPOS_GESTAO

    def form_valid(self, form):
        messages.success(self.request, 'Vídeo removido.')
        return super().form_valid(form)
