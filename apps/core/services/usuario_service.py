from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


@transaction.atomic
def criar(email: str, nome: str, password: str, **extra_fields) -> User:
    return User.objects.create_user(email=email, nome=nome, password=password, **extra_fields)


@transaction.atomic
def editar(usuario: User, dados: dict) -> User:
    for campo, valor in dados.items():
        setattr(usuario, campo, valor)
    usuario.save()
    return usuario


@transaction.atomic
def desativar(usuario: User) -> None:
    usuario.is_active = False
    usuario.save(update_fields=['is_active'])


@transaction.atomic
def reativar(usuario: User) -> None:
    usuario.is_active = True
    usuario.save(update_fields=['is_active'])


@transaction.atomic
def trocar_email(usuario: User, novo_email: str) -> User:
    usuario.email = User.objects.normalize_email(novo_email)
    usuario.save(update_fields=['email'])
    return usuario
