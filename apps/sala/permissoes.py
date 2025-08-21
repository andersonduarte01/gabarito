from rest_framework.permissions import BasePermission

from ..escola.models import UnidadeEscolar


class IsUnidadeEscolar(BasePermission):
    """
    Permite acesso apenas a usuários do tipo UnidadeEscolar
    """
    def has_permission(self, request, view):
        return isinstance(request.user, UnidadeEscolar)