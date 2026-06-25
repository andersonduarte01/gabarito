class CodigoModulo:
    # Obrigatórios — sempre ativos, fazem parte do Core
    ESCOLA       = 'escola'
    DIRETOR      = 'diretor'
    FUNCIONARIOS = 'funcionarios'
    PROFESSORES  = 'professores'
    ALUNOS       = 'alunos'
    TURMAS       = 'turmas'
    SERIES       = 'series'

    # Opcionais — ativáveis por escola dentro do plano
    FINANCEIRO_ESCOLAR = 'financeiro_escolar'
    FREQUENCIA         = 'frequencia'
    AVALIACOES         = 'avaliacoes'
    BOLETIM            = 'boletim'
    COMUNICADOS        = 'comunicados'
    RELATORIOS         = 'relatorios'
    RESPONSAVEIS       = 'responsaveis'


MODULOS_OBRIGATORIOS = frozenset({
    CodigoModulo.ESCOLA,
    CodigoModulo.DIRETOR,
    CodigoModulo.FUNCIONARIOS,
    CodigoModulo.PROFESSORES,
    CodigoModulo.ALUNOS,
    CodigoModulo.TURMAS,
    CodigoModulo.SERIES,
})

MODULOS_OPCIONAIS = frozenset({
    CodigoModulo.FINANCEIRO_ESCOLAR,
    CodigoModulo.FREQUENCIA,
    CodigoModulo.AVALIACOES,
    CodigoModulo.BOLETIM,
    CodigoModulo.COMUNICADOS,
    CodigoModulo.RELATORIOS,
    CodigoModulo.RESPONSAVEIS,
})
