from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .models import UsuarioEscola


# ---------------------------------------------------------------------------
# Views públicas
# ---------------------------------------------------------------------------

class Index(TemplateView):
    template_name = 'core/index.html'


class Contato(TemplateView):
    template_name = 'core/contate_nos.html'


class Sobre(TemplateView):
    template_name = 'core/sobre.html'


# ---------------------------------------------------------------------------
# Base para dashboards autenticados
# ---------------------------------------------------------------------------

class BaseDashboardView(TemplateView):
    """
    Classe base para todas as views de dashboard do sistema.

    Garante, em toda requisição:
      1. Usuário autenticado
      2. Contexto de escola injetado pelo EscolaMiddleware (request.escola + request.vinculo)
      3. Tipo de usuário autorizado conforme tipo_permitido

    Injeta automaticamente no contexto do template:
      {{ escola }}   — UnidadeEscolar atual da sessão
      {{ vinculo }}  — UsuarioEscola com tipo e status do vínculo
      {{ usuario }}  — Usuário logado

    Uso:
        class ProfessorDashboard(BaseDashboardView):
            template_name = 'professor/dashboard.html'
            tipo_permitido = [UsuarioEscola.PROFESSOR]

        # Acesso multi-perfil (ex.: diretor também pode ver o painel do colaborador)
        class ColaboradorDashboard(BaseDashboardView):
            template_name = 'colaborador/dashboard.html'
            tipo_permitido = [UsuarioEscola.COLABORADOR, UsuarioEscola.DIRETOR]

        # Sem restrição de tipo — qualquer vínculo ativo tem acesso
        class PainelGeral(BaseDashboardView):
            template_name = 'geral/painel.html'
            tipo_permitido = []
    """

    template_name: str | None = None
    tipo_permitido: list = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        escola = getattr(request, 'escola', None)
        vinculo = getattr(request, 'vinculo', None)

        if escola is None or vinculo is None:
            return redirect('escola:selecionar')

        if self.tipo_permitido and vinculo.tipo_usuario not in self.tipo_permitido:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['escola'] = self.request.escola
        context['vinculo'] = self.request.vinculo
        context['usuario'] = self.request.user
        context['tem_multiplas_escolas'] = getattr(
            self.request, 'tem_multiplas_escolas', False
        )
        return context


# ---------------------------------------------------------------------------
# Views comentadas — dependem de apps desativados temporariamente.
# Serão restauradas quando os módulos forem reativados.
# ---------------------------------------------------------------------------

# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.db.models import Q
# from django.views.generic import ListView
# from ..arquivos.models import Arquivo, Livro, Categoria
# from ..blog.models import Video
# from ..sala.models import Ano

# class Eventos(LoginRequiredMixin, TemplateView):
#     template_name = 'core/tutoriais.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['videos'] = Video.objects.all().order_by('-data_atualizada')
#         return context

# class Biblioteca(TemplateView):
#     template_name = 'core/biblioteca_novo.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['livros'] = Livro.objects.all().order_by('-data_modificacao')
#         context['categorias'] = Categoria.objects.all().order_by('categoria')
#         return context

# class Arquivos(TemplateView):
#     template_name = 'core/arquivos.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['arquivos'] = Arquivo.objects.all().order_by('-data_modificacao')
#         return context

# class PesquisarArquivo(ListView):
#     model = Arquivo
#     template_name = 'core/arquivos_resultado.html'
#     context_object_name = 'arquivos'
#     def get_queryset(self):
#         return Arquivo.objects.filter(titulo__icontains=self.request.GET.get("q"))

# class PesquisarLivro(ListView):
#     model = Livro
#     template_name = 'core/biblioteca_resultado.html'
#     context_object_name = 'livros'
#     def get_queryset(self):
#         return Livro.objects.filter(titulo__icontains=self.request.GET.get("q"))

# class PesquisarVideo(LoginRequiredMixin, ListView):
#     model = Video
#     template_name = 'core/tutoriais_resultado.html'
#     context_object_name = 'videos'
#     def get_queryset(self):
#         return Video.objects.filter(titulo__icontains=self.request.GET.get("q"))

# class AnoMateria(LoginRequiredMixin, ListView):
#     model = Video
#     template_name = 'core/tutoriais00.html'
#     context_object_name = 'videos'
#     def get_queryset(self):
#         periodo = self.kwargs['ano']
#         mapa = {
#             '1Ano': '1º Ano', '2Ano': '2º Ano', '3Ano': '3º Ano',
#             '4Ano': '4º Ano', '5Ano': '5º Ano', '6Ano': '6º Ano',
#             '7Ano': '7º Ano', '8Ano': '8º Ano', '9Ano': '9º Ano',
#         }
#         descricao = mapa.get(periodo, 'Educação Infantil')
#         ano = Ano.objects.get(descricao=descricao)
#         return Video.objects.filter(ano=ano, sigla=self.kwargs['sigla'])
