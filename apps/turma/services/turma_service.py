from django.db import transaction

from apps.turma.models import Turma


@transaction.atomic
def criar(escola, ano_letivo, serie, dados: dict) -> Turma:
    return Turma.objects.create(
        escola=escola,
        ano_letivo=ano_letivo,
        serie=serie,
        **dados,
    )


def editar(turma: Turma, dados: dict) -> Turma:
    for campo, valor in dados.items():
        setattr(turma, campo, valor)
    turma.save()
    return turma


def desativar(turma: Turma) -> None:
    turma.ativo = False
    turma.save(update_fields=['ativo'])


def reativar(turma: Turma) -> None:
    turma.ativo = True
    turma.save(update_fields=['ativo'])
