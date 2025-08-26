# caminho sugerido: seu_app/management/commands/populate_frequencia.py

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from apps.frequencia.models import Frequencia, FrequenciaAluno
from apps.sala.models import *

class Command(BaseCommand):
    help = "Popula a tabela Frequencia com base nos registros existentes de FrequenciaAluno"

    def handle(self, *args, **kwargs):
        # Agrupa frequencias por sala e data, contando presentes
        agrupamento = (
            FrequenciaAluno.objects
            .values('aluno__sala', 'data')
            .annotate(presentes=Count('id', filter=Q(presente=True)))
        )

        total_registros = 0
        for item in agrupamento:
            sala_id = item['aluno__sala']
            data_frequencia = item['data']
            presentes = item['presentes']

            # Cria ou atualiza a frequência da sala
            frequencia, created = Frequencia.objects.update_or_create(
                sala_id=sala_id,
                data=data_frequencia,
                defaults={'presentes': presentes, 'status': True}
            )

            total_registros += 1

        self.stdout.write(self.style.SUCCESS(
            f'Processo concluído! Total de registros processados: {total_registros}'
        ))
