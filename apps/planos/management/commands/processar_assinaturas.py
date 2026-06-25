from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.planos.models import AssinaturaEscola, StatusAssinatura
from apps.planos.services import assinatura_service


class Command(BaseCommand):
    help = 'Processa transições de status de assinaturas (executar diariamente via cron/task scheduler)'

    def handle(self, *args, **options):
        hoje = date.today()

        # TRIAL → TRIAL_EXPIRADO (prazo esgotado)
        for ass in AssinaturaEscola.objects.filter(status=StatusAssinatura.TRIAL):
            prazo = ass.data_inicio_trial + timedelta(days=ass.duracao_trial_dias)
            if hoje > prazo:
                assinatura_service.expirar_trial(ass)
                self.stdout.write(f'[TRIAL_EXPIRADO] {ass.escola}')

        # ATIVA → GRACE (data_vencimento atingida)
        for ass in AssinaturaEscola.objects.filter(
            status=StatusAssinatura.ATIVA,
            data_vencimento__lt=hoje,
        ):
            assinatura_service.iniciar_grace(ass, usuario=None)
            self.stdout.write(f'[GRACE] {ass.escola} — venceu em {ass.data_vencimento}')

        # GRACE → SUSPENSA (data_grace_fim atingida)
        for ass in AssinaturaEscola.objects.filter(
            status=StatusAssinatura.GRACE,
            data_grace_fim__lt=hoje,
        ):
            assinatura_service.suspender(ass, usuario=None, observacao='Carência encerrada.')
            self.stdout.write(f'[SUSPENSA] {ass.escola}')

        # TODO (Módulo 04 — Notificações): alertas de grace D+0/5/10/14/15
        # Os alertas serão disparados via notificacao_service.criar() quando
        # o módulo de notificações estiver implementado.

        self.stdout.write(self.style.SUCCESS('Assinaturas processadas com sucesso.'))
