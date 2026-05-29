import os

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseForbidden

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def serve_media_protegida(request, path):
    """
    Serve arquivos de mídia com autenticação obrigatória.

    Aceita duas formas de autenticação:
      - Sessão web  : usuário logado normalmente (request.user.is_authenticated)
      - JWT Bearer  : cabeçalho Authorization: Bearer <token>  (app mobile)

    Proteções aplicadas:
      - Autenticação dupla (sessão ou JWT)
      - Validação de path traversal via os.path.realpath()
      - Verificação de existência do arquivo antes de servir

    Uso em urls.py:
        path('media/<path:path>', serve_media_protegida, name='media_protegida'),

    Nota de produção:
        Em ambiente com Nginx, prefira X-Accel-Redirect no lugar de
        FileResponse para não passar o arquivo pelo processo Django:

        response = HttpResponse()
        response['X-Accel-Redirect'] = f'/protected-media/{path}'
        response['Content-Type'] = ''
        return response
    """
    usuario = _autenticar(request)
    if usuario is None:
        return HttpResponseForbidden('Autenticação necessária para acessar este arquivo.')

    caminho_absoluto = _validar_caminho(path)
    if caminho_absoluto is None:
        raise Http404

    if not os.path.isfile(caminho_absoluto):
        raise Http404

    return FileResponse(open(caminho_absoluto, 'rb'))


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _autenticar(request):
    """
    Retorna o usuário autenticado via sessão ou JWT.
    Retorna None se nenhuma forma de autenticação for válida.
    """
    if request.user.is_authenticated:
        return request.user

    return _autenticar_jwt(request)


def _autenticar_jwt(request):
    """
    Valida o token JWT do cabeçalho Authorization: Bearer <token>.
    Retorna o usuário ou None se o token for inválido/ausente.
    """
    cabecalho = request.headers.get('Authorization', '')
    if not cabecalho.startswith('Bearer '):
        return None

    try:
        autenticador = JWTAuthentication()
        resultado = autenticador.authenticate(request)
        if resultado is None:
            return None
        usuario, _ = resultado
        return usuario
    except (InvalidToken, TokenError):
        return None


def _validar_caminho(path: str) -> str | None:
    """
    Resolve o caminho real do arquivo e garante que está dentro de MEDIA_ROOT.
    Rejeita path traversal (../../), symlinks fora da raiz e caminhos absolutos.
    Retorna o caminho absoluto validado ou None se inválido.
    """
    media_root = os.path.realpath(settings.MEDIA_ROOT)
    caminho_candidato = os.path.realpath(os.path.join(media_root, path))

    if not caminho_candidato.startswith(media_root + os.sep):
        return None

    return caminho_candidato
