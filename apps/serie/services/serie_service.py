from django.db import transaction

SERIES_PADRAO = {
    'INF': ['Berçário', 'Maternal I', 'Maternal II', 'Pré I', 'Pré II'],
    'FI':  ['1º Ano', '2º Ano', '3º Ano', '4º Ano', '5º Ano'],
    'FII': ['6º Ano', '7º Ano', '8º Ano', '9º Ano'],
    'MED': ['1ª Série', '2ª Série', '3ª Série'],
    'TEC': ['1º Módulo', '2º Módulo', '3º Módulo'],
}


@transaction.atomic
def criar_series_padrao(escola, segmento) -> None:
    """Popula as séries padrão ao adicionar um segmento à escola."""
    from apps.serie.models import Serie
    nomes = SERIES_PADRAO.get(segmento.tipo, [])
    for ordem, nome in enumerate(nomes, start=1):
        Serie.objects.get_or_create(
            escola=escola,
            segmento=segmento,
            nome=nome,
            defaults={'ordem': ordem},
        )


def criar(escola, segmento, dados: dict):
    from apps.serie.models import Serie
    return Serie.objects.create(escola=escola, segmento=segmento, **dados)


def editar(serie, dados: dict):
    for campo, valor in dados.items():
        setattr(serie, campo, valor)
    serie.save()
    return serie


def desativar(serie) -> None:
    serie.ativo = False
    serie.save(update_fields=['ativo'])


def reativar(serie) -> None:
    serie.ativo = True
    serie.save(update_fields=['ativo'])
