from django.db import transaction

from apps.core.models import TipoVinculo
from apps.core.services import vinculo_service
from apps.diretor.models import CargoDiretor, PerfilDiretor


@transaction.atomic
def criar(escola, usuario_dados: dict, perfil_dados: dict, criado_por) -> PerfilDiretor:
    """Cria ou reutiliza Usuario + VinculoEscola + PapelVinculo(DIRETOR) + PerfilDiretor."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    usuario, _ = User.objects.get_or_create(
        email=usuario_dados['email'],
        defaults={'nome': usuario_dados['nome'], 'is_active': True},
    )

    vinculo = vinculo_service.criar_vinculo(usuario, escola)
    papel   = vinculo_service.adicionar_papel(vinculo, TipoVinculo.DIRETOR)

    perfil = PerfilDiretor.objects.create(
        papel=papel,
        cargo=perfil_dados.get('cargo', CargoDiretor.TITULAR),
        cpf=perfil_dados.get('cpf', ''),
        data_nascimento=perfil_dados.get('data_nascimento'),
        telefone=perfil_dados.get('telefone', ''),
        data_inicio=perfil_dados.get('data_inicio'),
    )
    return perfil


def editar(perfil: PerfilDiretor, dados: dict) -> PerfilDiretor:
    for campo, valor in dados.items():
        setattr(perfil, campo, valor)
    perfil.save()
    return perfil


@transaction.atomic
def desativar(papel, desativado_por) -> None:
    from apps.core.services.vinculo_service import remover_papel
    remover_papel(papel)


@transaction.atomic
def salvar_endereco(perfil: PerfilDiretor, dados: dict) -> PerfilDiretor:
    from apps.core.models import Endereco
    if perfil.endereco_id:
        for campo, valor in dados.items():
            setattr(perfil.endereco, campo, valor)
        perfil.endereco.save()
    else:
        endereco = Endereco.objects.create(**dados)
        perfil.endereco = endereco
        perfil.save(update_fields=['endereco'])
    return perfil
