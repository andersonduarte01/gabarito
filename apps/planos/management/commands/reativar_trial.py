"""
Reativa o trial de todas as escolas bloqueadas (TRIAL_EXPIRADO)
ou estende o trial das que ainda estão em TRIAL.

Uso:
    python manage.py reativar_trial
    python manage.py reativar_trial --dias 365
    python manage.py reativar_trial --escola "Nome da Escola"
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.planos.models import AssinaturaEscola, HistoricoAssinatura, StatusAssinatura


class Command(BaseCommand):
    help = 'Reativa trial expirado das escolas ou estende trial vigente'

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=365,
                            help='Duração do trial em dias (padrão: 365)')
        parser.add_argument('--escola', type=str, default=None,
                            help='Nome parcial da escola (filtra apenas ela)')

    def handle(self, *args, **options):
        dias = options['dias']
        escola_nome = options['escola']

        qs = AssinaturaEscola.objects.select_related('escola').filter(
            status__in=[StatusAssinatura.TRIAL, StatusAssinatura.TRIAL_EXPIRADO]
        )
        if escola_nome:
            qs = qs.filter(escola__nome__icontains=escola_nome)

        if not qs.exists():
            self.stdout.write(self.style.WARNING('Nenhuma assinatura em TRIAL ou TRIAL_EXPIRADO encontrada.'))
            return

        for assinatura in qs:
            status_anterior = assinatura.status
            assinatura.status = StatusAssinatura.TRIAL
            assinatura.data_inicio_trial = date.today()
            assinatura.duracao_trial_dias = dias
            assinatura.save(update_fields=['status', 'data_inicio_trial', 'duracao_trial_dias'])

            HistoricoAssinatura.objects.create(
                assinatura=assinatura,
                status_anterior=status_anterior,
                status_novo=StatusAssinatura.TRIAL,
                observacao=f'Trial reativado via management command. Duração: {dias} dias.',
            )
            self.stdout.write(self.style.SUCCESS(
                f'[OK] {assinatura.escola} — {status_anterior} → TRIAL ({dias} dias)'
            ))
