from django.db import transaction

from apps.configuracao.models import (
    ConfiguracaoAcademica,
    ConfiguracaoFrequencia,
    ConfiguracaoProfessor,
)


@transaction.atomic
def criar_configuracoes_padrao(escola) -> None:
    """Cria os três modelos de configuração com valores padrão. Chamado por EscolaService.criar()."""
    ConfiguracaoAcademica.objects.get_or_create(escola=escola)
    ConfiguracaoFrequencia.objects.get_or_create(escola=escola)
    ConfiguracaoProfessor.objects.get_or_create(escola=escola)


def atualizar_academica(escola, dados: dict) -> ConfiguracaoAcademica:
    config = escola.configuracao_academica
    for campo, valor in dados.items():
        setattr(config, campo, valor)
    config.save()
    return config


def atualizar_frequencia(escola, dados: dict) -> ConfiguracaoFrequencia:
    config = escola.configuracao_frequencia
    for campo, valor in dados.items():
        setattr(config, campo, valor)
    config.save()
    return config


def atualizar_professor(escola, dados: dict) -> ConfiguracaoProfessor:
    config = escola.configuracao_professor
    for campo, valor in dados.items():
        setattr(config, campo, valor)
    config.save()
    return config
