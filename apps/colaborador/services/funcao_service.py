from django.db import transaction

from apps.colaborador.models import FuncaoEscolar


@transaction.atomic
def criar(escola, nome: str) -> FuncaoEscolar:
    funcao, created = FuncaoEscolar.objects.get_or_create(
        escola=escola,
        nome=nome.strip(),
        defaults={'ativo': True},
    )
    if not created and not funcao.ativo:
        funcao.ativo = True
        funcao.save(update_fields=['ativo'])
    return funcao


def editar(funcao: FuncaoEscolar, nome: str) -> FuncaoEscolar:
    funcao.nome = nome.strip()
    funcao.save(update_fields=['nome'])
    return funcao


def desativar(funcao: FuncaoEscolar) -> None:
    funcao.ativo = False
    funcao.save(update_fields=['ativo'])


def reativar(funcao: FuncaoEscolar) -> None:
    funcao.ativo = True
    funcao.save(update_fields=['ativo'])
