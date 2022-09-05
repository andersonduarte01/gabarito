from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from unidecode import unidecode
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from ..blog.models import Blog, Categoria
from ..escola.models import UnidadeEscolar


class Noticias(ListView):
    model = Blog
    template_name = 'blog/blog.html'
    context_object_name = 'noticias'

    def get_queryset(self):
        return Blog.objects.filter().order_by('-data')


class Noticia(LoginRequiredMixin, DetailView):
    model = Blog
    template_name = 'blog/noticia.html'
    context_object_name = 'noticia'

    def get_absolute_url(self):
        return reverse('blog:noticia', kwargs={'slug': self.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temas = Categoria.objects.all()
        noticias = Blog.objects.filter().order_by('-data')
        recentes = noticias[:2]
        context['temas'] = temas
        context['recentes'] = recentes
        return context


class AddNoticia(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ('titulo', 'imagem', 'conteudo', 'categoria')
    template_name = 'blog/add_noticia.html'
    success_url = '/blog/'

    def form_valid(self, form):
        noticia = form.save(commit=False)
        x = noticia.titulo.replace(' ', '-')
        print(x)
        notice = unidecode(x)
        print(notice)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        noticia.autor = escola
        noticia.slug = notice.lower()
        noticia.save()
        return super().form_valid(form)


class EditNoticia(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ('titulo', 'imagem', 'conteudo', 'categoria')
    template_name = 'blog/add_noticia.html'
    success_url = '/blog/'

