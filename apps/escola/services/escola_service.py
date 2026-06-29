from django.db import transaction

from apps.escola.models import EnderecoEscolar, SegmentoEscolar, UnidadeEscolar


@transaction.atomic
def criar(dados: dict, usuario=None) -> UnidadeEscolar:
    """Cria UnidadeEscolar, inicia trial e cria configurações padrão automaticamente."""
    from apps.planos.services import assinatura_service
    from apps.configuracao.services.configuracao_service import criar_configuracoes_padrao
    from apps.materia.services.materia_service import criar_materias_padrao
    escola = UnidadeEscolar.objects.create(**dados)
    assinatura_service.iniciar_trial(escola, usuario)
    criar_configuracoes_padrao(escola)
    criar_materias_padrao(escola)
    return escola


def atualizar(escola: UnidadeEscolar, dados: dict) -> UnidadeEscolar:
    for campo, valor in dados.items():
        setattr(escola, campo, valor)
    escola.save()
    return escola


@transaction.atomic
def adicionar_endereco(escola: UnidadeEscolar, dados: dict) -> EnderecoEscolar:
    return EnderecoEscolar.objects.create(escola=escola, **dados)


@transaction.atomic
def definir_endereco_principal(endereco: EnderecoEscolar) -> None:
    """Remove o principal anterior, define o novo e sincroniza municipio/uf na escola."""
    EnderecoEscolar.objects.filter(escola=endereco.escola, principal=True).update(principal=False)
    endereco.principal = True
    endereco.save(update_fields=['principal'])
    endereco.escola.municipio = endereco.municipio
    endereco.escola.uf = endereco.uf
    endereco.escola.save(update_fields=['municipio', 'uf'])


def atualizar_endereco(endereco: EnderecoEscolar, dados: dict) -> EnderecoEscolar:
    for campo, valor in dados.items():
        setattr(endereco, campo, valor)
    endereco.save()
    return endereco


@transaction.atomic
def remover_endereco(endereco: EnderecoEscolar) -> None:
    if endereco.principal:
        endereco.escola.municipio = ''
        endereco.escola.uf = ''
        endereco.escola.save(update_fields=['municipio', 'uf'])
    endereco.delete()


@transaction.atomic
def adicionar_segmento(escola: UnidadeEscolar, tipo: str) -> SegmentoEscolar:
    from apps.serie.services.serie_service import criar_series_padrao
    segmento = SegmentoEscolar.objects.create(escola=escola, tipo=tipo)
    criar_series_padrao(escola, segmento)
    return segmento


def remover_segmento(segmento: SegmentoEscolar) -> None:
    segmento.delete()
