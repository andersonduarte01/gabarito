from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.core.models import UsuarioEscola
from apps.core.permissao import PermissaoRequiredMixin
from .forms import NoticiaForm
from .models import Noticia, Categoria

_TIPOS_GESTAO = [UsuarioEscola.DIRETOR, UsuarioEscola.COLABORADOR]
_TIPOS_EDICAO = [UsuarioEscola.DIRETOR]


def _qs_publicas(request):
    """Retorna queryset de notícias visíveis ao visitante atual."""
    escola_id = request.session.get('escola_id')
    qs = Noticia.publicados.select_related('categoria', 'autor')
    if escola_id:
        return qs.filter(
            Q(visibilidade=Noticia.PUBLICA)
            | Q(visibilidade=Noticia.PRIVADA, escola_id=escola_id)
        )
    return qs.filter(visibilidade=Noticia.PUBLICA)


class BlogGestaoMixin:
    """
    Injeta request.escola a partir da sessão quando o EscolaMiddleware não rodou
    (rotas sob /blog/ estão em PREFIXOS_IGNORADOS para permitir acesso público).
    """

    def dispatch(self, request, *args, **kwargs):
        if not getattr(request, 'escola', None):
            from apps.escola.models import UnidadeEscolar
            escola_id = request.session.get('escola_id')
            if escola_id:
                try:
                    request.escola = UnidadeEscolar.objects.get(pk=escola_id, ativo=True)
                except UnidadeEscolar.DoesNotExist:
                    pass
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Views públicas
# ---------------------------------------------------------------------------

class NoticiaLista(ListView):
    model = Noticia
    template_name = 'blog/blog.html'
    context_object_name = 'noticias'
    paginate_by = 9

    def get_queryset(self):
        qs = _qs_publicas(self.request).order_by('-destaque', '-criado_em')
        categoria_slug = self.request.GET.get('categoria', '').strip()
        if categoria_slug:
            qs = qs.filter(categoria__slug=categoria_slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['categoria_ativa'] = self.request.GET.get('categoria', '')
        if not context['categoria_ativa'] and not self.request.GET.get('page'):
            context['destaque_post'] = (
                _qs_publicas(self.request)
                .filter(destaque=True)
                .order_by('-criado_em')
                .first()
            )
        return context


class NoticiaDetalhe(DetailView):
    model = Noticia
    template_name = 'blog/noticia.html'
    context_object_name = 'noticia'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return _qs_publicas(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['temas'] = Categoria.objects.all()
        context['recentes'] = (
            _qs_publicas(self.request)
            .exclude(pk=self.object.pk)
            .order_by('-criado_em')[:3]
        )
        return context


class NoticiaPesquisa(ListView):
    model = Noticia
    template_name = 'blog/blog_resultado.html'
    context_object_name = 'noticias'
    paginate_by = 9

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Noticia.objects.none()
        return (
            _qs_publicas(self.request)
            .filter(
                Q(titulo__icontains=query)
                | Q(resumo__icontains=query)
                | Q(conteudo__icontains=query)
            )
            .order_by('-criado_em')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


# ---------------------------------------------------------------------------
# Views de gerenciamento (autenticadas e permissionadas)
# ---------------------------------------------------------------------------

class GerenciarNoticias(BlogGestaoMixin, PermissaoRequiredMixin, ListView):
    model = Noticia
    template_name = 'blog/gerenciar.html'
    context_object_name = 'noticias'
    paginate_by = 20
    permissao_tipos = _TIPOS_GESTAO

    def get_queryset(self):
        qs = (
            Noticia.objects
            .filter(escola=self.request.escola)
            .select_related('categoria', 'autor')
            .order_by('-criado_em')
        )
        status = self.request.GET.get('status', '').strip()
        if status in (Noticia.PUBLICADO, Noticia.RASCUNHO):
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_ativo'] = self.request.GET.get('status', '')
        base = Noticia.objects.filter(escola=self.request.escola)
        context['total_publicados'] = base.filter(status=Noticia.PUBLICADO).count()
        context['total_rascunhos'] = base.filter(status=Noticia.RASCUNHO).count()
        return context


class CriarNoticia(BlogGestaoMixin, PermissaoRequiredMixin, CreateView):
    model = Noticia
    form_class = NoticiaForm
    template_name = 'blog/add_noticia.html'
    success_url = reverse_lazy('blog:gerenciar')
    permissao_tipos = _TIPOS_GESTAO
    extra_context = {'titulo': 'Publicar notícia'}

    def form_valid(self, form):
        form.instance.autor = self.request.user
        form.instance.escola = self.request.escola
        messages.success(self.request, 'Notícia criada com sucesso.')
        return super().form_valid(form)


class EditarNoticia(BlogGestaoMixin, PermissaoRequiredMixin, UpdateView):
    model = Noticia
    form_class = NoticiaForm
    template_name = 'blog/add_noticia.html'
    success_url = reverse_lazy('blog:gerenciar')
    permissao_tipos = _TIPOS_GESTAO
    extra_context = {'titulo': 'Editar notícia'}

    def get_queryset(self):
        qs = Noticia.objects.filter(escola=self.request.escola)
        if self.request.vinculo.tipo_usuario == UsuarioEscola.COLABORADOR:
            qs = qs.filter(autor=self.request.user)
        return qs

    def form_valid(self, form):
        messages.success(self.request, 'Notícia atualizada.')
        return super().form_valid(form)


class ExcluirNoticia(BlogGestaoMixin, PermissaoRequiredMixin, DeleteView):
    model = Noticia
    template_name = 'blog/confirmar_exclusao.html'
    success_url = reverse_lazy('blog:gerenciar')
    permissao_tipos = _TIPOS_EDICAO

    def get_queryset(self):
        return Noticia.objects.filter(escola=self.request.escola)

    def form_valid(self, form):
        messages.success(self.request, 'Notícia excluída.')
        return super().form_valid(form)


class AlternarStatusNoticia(BlogGestaoMixin, PermissaoRequiredMixin, View):
    permissao_tipos = _TIPOS_GESTAO

    def post(self, request, pk):
        noticia = get_object_or_404(Noticia, pk=pk, escola=request.escola)
        if noticia.status == Noticia.PUBLICADO:
            noticia.status = Noticia.RASCUNHO
            msg = 'Notícia movida para rascunhos.'
        else:
            noticia.status = Noticia.PUBLICADO
            msg = 'Notícia publicada com sucesso.'
        noticia.save(update_fields=['status', 'atualizado_em'])
        messages.success(request, msg)
        return redirect('blog:gerenciar')
