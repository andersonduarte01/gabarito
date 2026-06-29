from django.db import transaction


class AnoLetivoError(Exception):
    pass


def criar(escola, dados, criado_por):
    from apps.ano_letivo.models import AnoLetivo, StatusAnoLetivo
    if AnoLetivo.objects.filter(escola=escola, ano=dados['ano']).exists():
        raise AnoLetivoError(f'Já existe um ano letivo {dados["ano"]} para esta escola.')
    if dados['data_inicio'] >= dados['data_fim']:
        raise AnoLetivoError('A data de início deve ser anterior à data de fim.')
    return AnoLetivo.objects.create(
        escola      = escola,
        ano         = dados['ano'],
        data_inicio = dados['data_inicio'],
        data_fim    = dados['data_fim'],
        status      = StatusAnoLetivo.EM_PLANEJAMENTO,
        criado_por  = criado_por,
    )


@transaction.atomic
def iniciar(ano_letivo, usuario):
    from apps.ano_letivo.models import AnoLetivo, StatusAnoLetivo
    if ano_letivo.status != StatusAnoLetivo.EM_PLANEJAMENTO:
        raise AnoLetivoError('Apenas anos em planejamento podem ser iniciados.')
    conflito = (
        AnoLetivo.objects
        .select_for_update()
        .filter(escola=ano_letivo.escola, status=StatusAnoLetivo.EM_ANDAMENTO)
        .exclude(pk=ano_letivo.pk)
        .exists()
    )
    if conflito:
        raise AnoLetivoError('Já existe um ano letivo em andamento para esta escola.')
    ano_letivo.status = StatusAnoLetivo.EM_ANDAMENTO
    ano_letivo.save(update_fields=['status', 'atualizado_em'])


@transaction.atomic
def encerrar(ano_letivo, usuario):
    from apps.ano_letivo.models import StatusAnoLetivo
    if ano_letivo.status != StatusAnoLetivo.EM_ANDAMENTO:
        raise AnoLetivoError('Apenas anos em andamento podem ser encerrados.')
    ano_letivo.status = StatusAnoLetivo.ENCERRADO
    ano_letivo.save(update_fields=['status', 'atualizado_em'])


def criar_periodo(ano_letivo, dados):
    from apps.ano_letivo.models import PeriodoLetivo, StatusAnoLetivo
    if ano_letivo.status == StatusAnoLetivo.ENCERRADO:
        raise AnoLetivoError('Não é possível adicionar períodos a um ano encerrado.')
    data_inicio = dados['data_inicio']
    data_fim    = dados['data_fim']
    if data_inicio < ano_letivo.data_inicio or data_fim > ano_letivo.data_fim:
        raise AnoLetivoError(
            f'As datas do período devem estar dentro do ano letivo '
            f'({ano_letivo.data_inicio:%d/%m/%Y} a {ano_letivo.data_fim:%d/%m/%Y}).'
        )
    _verificar_sobreposicao(ano_letivo, data_inicio, data_fim)
    return PeriodoLetivo.objects.create(
        ano_letivo  = ano_letivo,
        numero      = dados['numero'],
        nome        = dados['nome'],
        data_inicio = data_inicio,
        data_fim    = data_fim,
    )


def editar_periodo(periodo, dados):
    from apps.ano_letivo.models import StatusAnoLetivo
    ano_letivo = periodo.ano_letivo
    if ano_letivo.status == StatusAnoLetivo.ENCERRADO:
        raise AnoLetivoError('Não é possível editar períodos de um ano encerrado.')
    data_inicio = dados['data_inicio']
    data_fim    = dados['data_fim']
    if data_inicio < ano_letivo.data_inicio or data_fim > ano_letivo.data_fim:
        raise AnoLetivoError(
            f'As datas do período devem estar dentro do ano letivo '
            f'({ano_letivo.data_inicio:%d/%m/%Y} a {ano_letivo.data_fim:%d/%m/%Y}).'
        )
    _verificar_sobreposicao(ano_letivo, data_inicio, data_fim, excluir_pk=periodo.pk)
    periodo.numero      = dados['numero']
    periodo.nome        = dados['nome']
    periodo.data_inicio = data_inicio
    periodo.data_fim    = data_fim
    periodo.save()


def remover_periodo(periodo):
    from apps.ano_letivo.models import StatusAnoLetivo
    if periodo.ano_letivo.status == StatusAnoLetivo.ENCERRADO:
        raise AnoLetivoError('Não é possível remover períodos de um ano encerrado.')
    periodo.delete()


def _verificar_sobreposicao(ano_letivo, data_inicio, data_fim, excluir_pk=None):
    from apps.ano_letivo.models import PeriodoLetivo
    qs = PeriodoLetivo.objects.filter(
        ano_letivo  = ano_letivo,
        data_inicio__lt = data_fim,
        data_fim__gt    = data_inicio,
    )
    if excluir_pk:
        qs = qs.exclude(pk=excluir_pk)
    if qs.exists():
        raise AnoLetivoError('As datas do período se sobrepõem com um período já existente.')
