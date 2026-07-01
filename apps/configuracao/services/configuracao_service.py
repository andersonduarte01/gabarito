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


def obter_academica(escola) -> ConfiguracaoAcademica:
    config, _ = ConfiguracaoAcademica.objects.get_or_create(escola=escola)
    return config


def obter_frequencia(escola) -> ConfiguracaoFrequencia:
    config, _ = ConfiguracaoFrequencia.objects.get_or_create(escola=escola)
    return config


def obter_professor(escola) -> ConfiguracaoProfessor:
    config, _ = ConfiguracaoProfessor.objects.get_or_create(escola=escola)
    return config


def atualizar_academica(escola, dados: dict) -> ConfiguracaoAcademica:
    config = obter_academica(escola)
    for campo, valor in dados.items():
        setattr(config, campo, valor)
    config.save()
    return config


def atualizar_frequencia(escola, dados: dict) -> ConfiguracaoFrequencia:
    config = obter_frequencia(escola)
    for campo, valor in dados.items():
        setattr(config, campo, valor)
    config.save()
    return config


def atualizar_professor(escola, dados: dict) -> ConfiguracaoProfessor:
    config = obter_professor(escola)
    for campo, valor in dados.items():
        setattr(config, campo, valor)
    config.save()
    return config
