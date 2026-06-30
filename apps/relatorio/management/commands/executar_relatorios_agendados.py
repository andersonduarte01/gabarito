from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Executa os relatórios agendados para todas as escolas ativas.'

    def handle(self, *args, **options):
        from apps.escola.models import UnidadeEscolar
        from apps.relatorio.services import relatorio_service

        escolas = UnidadeEscolar.objects.all()
        total = 0
        for escola in escolas:
            gerados = relatorio_service.executar_agendados(escola)
            if gerados:
                self.stdout.write(f'  {escola.nome}: {gerados} relatório(s) gerado(s)')
                total += gerados

        self.stdout.write(self.style.SUCCESS(f'Total: {total} relatório(s) gerado(s).'))
