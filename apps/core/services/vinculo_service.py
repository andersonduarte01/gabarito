from django.db import transaction

from apps.core.models import VinculoEscola, PapelVinculo


@transaction.atomic
def criar_vinculo(usuario, escola) -> VinculoEscola:
    """Cria ou reativa um vínculo entre usuário e escola."""
    vinculo, _ = VinculoEscola.objects.get_or_create(usuario=usuario, escola=escola)
    if not vinculo.ativo:
        vinculo.ativo = True
        vinculo.save(update_fields=['ativo'])
    return vinculo


@transaction.atomic
def adicionar_papel(vinculo: VinculoEscola, tipo: str) -> PapelVinculo:
    """Adiciona um papel ao vínculo. Reativa se já existia inativo."""
    papel, criado = PapelVinculo.objects.get_or_create(vinculo=vinculo, tipo=tipo)
    if not criado and not papel.ativo:
        papel.ativo = True
        papel.save(update_fields=['ativo'])
    return papel


@transaction.atomic
def remover_papel(papel: PapelVinculo) -> None:
    """Desativa um papel. Se não restar papel ativo, desativa o vínculo."""
    papel.ativo = False
    papel.save(update_fields=['ativo'])
    if not papel.vinculo.papeis.filter(ativo=True).exists():
        papel.vinculo.ativo = False
        papel.vinculo.save(update_fields=['ativo'])


def listar_vinculos_ativos(usuario):
    return (
        VinculoEscola.objects
        .filter(usuario=usuario, ativo=True)
        .select_related('escola')
        .prefetch_related('papeis')
    )


def selecionar_papel(request, papel: PapelVinculo) -> None:
    """Persiste o papel ativo na sessão."""
    request.session['papel_id'] = papel.pk
