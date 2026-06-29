from django.db import transaction

from apps.core.models import TipoVinculo
from apps.core.services import vinculo_service
from apps.colaborador.models import PerfilColaborador


@transaction.atomic
def criar(escola, usuario_dados: dict, perfil_dados: dict, criado_por) -> PerfilColaborador:
    """Cria/reutiliza Usuario + VinculoEscola + PapelVinculo(FUNCIONARIO) + PerfilColaborador."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    usuario, _ = User.objects.get_or_create(
        email=usuario_dados['email'],
        defaults={'nome': usuario_dados['nome'], 'is_active': True},
    )

    vinculo = vinculo_service.criar_vinculo(usuario, escola)
    papel   = vinculo_service.adicionar_papel(vinculo, TipoVinculo.FUNCIONARIO)

    perfil = PerfilColaborador.objects.create(
        papel=papel,
        cpf=perfil_dados.get('cpf', ''),
        rg=perfil_dados.get('rg', ''),
        data_nascimento=perfil_dados.get('data_nascimento'),
        telefone=perfil_dados.get('telefone', ''),
        data_admissao=perfil_dados.get('data_admissao'),
        tipo_vinculo=perfil_dados.get('tipo_vinculo', 'CLT'),
        pis=perfil_dados.get('pis', ''),
        funcao=perfil_dados.get('funcao'),
    )
    return perfil


def editar(perfil: PerfilColaborador, dados: dict) -> PerfilColaborador:
    for campo, valor in dados.items():
        setattr(perfil, campo, valor)
    perfil.save()
    return perfil


@transaction.atomic
def desativar(papel, desativado_por) -> None:
    from apps.core.services.vinculo_service import remover_papel
    remover_papel(papel)


@transaction.atomic
def reativar(papel) -> None:
    papel.ativo = True
    papel.save(update_fields=['ativo'])


@transaction.atomic
def salvar_endereco(perfil: PerfilColaborador, dados: dict) -> PerfilColaborador:
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
