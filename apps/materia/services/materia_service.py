from django.db import transaction

MATERIAS_PADRAO = [
    'Lingua Portuguesa',
    'Matematica',
    'Ciencias',
    'Historia',
    'Geografia',
    'Arte',
    'Educacao Fisica',
    'Lingua Inglesa',
    'Biologia',
    'Fisica',
    'Quimica',
    'Filosofia',
    'Sociologia',
    'Educacao Religiosa',
]


@transaction.atomic
def criar_materias_padrao(escola) -> None:
    """Pool BNCC criado automaticamente ao criar a escola."""
    from apps.materia.models import Materia
    for nome in MATERIAS_PADRAO:
        Materia.objects.get_or_create(escola=escola, nome=nome)


def criar(escola, dados: dict):
    from apps.materia.models import Materia
    return Materia.objects.create(escola=escola, **dados)


def editar(materia, dados: dict):
    for campo, valor in dados.items():
        setattr(materia, campo, valor)
    materia.save()
    return materia


def desativar(materia) -> None:
    materia.ativo = False
    materia.save(update_fields=['ativo'])


def reativar(materia) -> None:
    materia.ativo = True
    materia.save(update_fields=['ativo'])


@transaction.atomic
def vincular_serie(materia, serie):
    from apps.materia.models import MateriaSerieConfig
    config, created = MateriaSerieConfig.objects.get_or_create(
        materia=materia,
        serie=serie,
        defaults={'ativo': True},
    )
    if not created and not config.ativo:
        config.ativo = True
        config.save(update_fields=['ativo'])
    return config


def desvincular_serie(config) -> None:
    config.ativo = False
    config.save(update_fields=['ativo'])
