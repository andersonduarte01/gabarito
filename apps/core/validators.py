import re

from django.core.exceptions import ValidationError


# ---------------------------------------------------------------------------
# Normalização
# ---------------------------------------------------------------------------

def normalizar_cpf(cpf: str | None) -> str | None:
    """Remove formatação do CPF. Retorna None se a entrada for vazia."""
    if not cpf:
        return None
    return re.sub(r'\D', '', cpf)


def normalizar_cnpj(cnpj: str | None) -> str | None:
    """Remove formatação do CNPJ. Retorna None se a entrada for vazia."""
    if not cnpj:
        return None
    return re.sub(r'\D', '', cnpj)


def normalizar_telefone(telefone: str | None) -> str | None:
    """Remove tudo exceto dígitos e o símbolo +. Retorna None se vazio."""
    if not telefone:
        return None
    return re.sub(r'[^\d+]', '', telefone)


# ---------------------------------------------------------------------------
# CPF
# ---------------------------------------------------------------------------

def _calcular_digito_cpf(digitos: list[int], peso_inicial: int) -> int:
    soma = sum(d * p for d, p in zip(digitos, range(peso_inicial, 1, -1)))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def validate_cpf(cpf: str) -> None:
    """
    Valida CPF limpo (somente dígitos, 11 caracteres).
    Levanta ValidationError se inválido.
    """
    if not cpf or not re.fullmatch(r'\d{11}', cpf):
        raise ValidationError(
            'CPF inválido. Informe exatamente 11 dígitos numéricos.',
            code='cpf_formato',
        )

    if len(set(cpf)) == 1:
        raise ValidationError(
            'CPF inválido.',
            code='cpf_sequencia',
        )

    digitos = [int(d) for d in cpf]

    primeiro = _calcular_digito_cpf(digitos[:9], peso_inicial=10)
    if primeiro != digitos[9]:
        raise ValidationError('CPF inválido.', code='cpf_digito1')

    segundo = _calcular_digito_cpf(digitos[:10], peso_inicial=11)
    if segundo != digitos[10]:
        raise ValidationError('CPF inválido.', code='cpf_digito2')


# ---------------------------------------------------------------------------
# CNPJ
# ---------------------------------------------------------------------------

_PESOS_CNPJ_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_PESOS_CNPJ_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


def _calcular_digito_cnpj(digitos: list[int], pesos: list[int]) -> int:
    soma = sum(d * p for d, p in zip(digitos, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def validate_cnpj(cnpj: str) -> None:
    """
    Valida CNPJ limpo (somente dígitos, 14 caracteres).
    Levanta ValidationError se inválido.
    """
    if not cnpj or not re.fullmatch(r'\d{14}', cnpj):
        raise ValidationError(
            'CNPJ inválido. Informe exatamente 14 dígitos numéricos.',
            code='cnpj_formato',
        )

    if len(set(cnpj)) == 1:
        raise ValidationError(
            'CNPJ inválido.',
            code='cnpj_sequencia',
        )

    digitos = [int(d) for d in cnpj]

    primeiro = _calcular_digito_cnpj(digitos[:12], _PESOS_CNPJ_1)
    if primeiro != digitos[12]:
        raise ValidationError('CNPJ inválido.', code='cnpj_digito1')

    segundo = _calcular_digito_cnpj(digitos[:13], _PESOS_CNPJ_2)
    if segundo != digitos[13]:
        raise ValidationError('CNPJ inválido.', code='cnpj_digito2')


# ---------------------------------------------------------------------------
# Telefone
# ---------------------------------------------------------------------------

def validate_telefone(telefone: str) -> None:
    """
    Valida telefone brasileiro (fixo ou celular), com ou sem DDD.
    Aceita somente dígitos, entre 10 e 11 caracteres.
    """
    limpo = normalizar_telefone(telefone) or ''
    if not re.fullmatch(r'\d{10,11}', limpo):
        raise ValidationError(
            'Telefone inválido. Informe DDD + número (10 ou 11 dígitos).',
            code='telefone_formato',
        )
