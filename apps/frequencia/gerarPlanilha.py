import datetime
from calendar import monthrange

from ..frequencia.models import Frequencia, FrequenciaAluno


def dias_mes(mes, ano):
    dias_mes_1 = []
    dia, mes_x = monthrange(ano, mes)
    for i in range(1, mes_x + 1):
        dia_semana = datetime.date(ano, mes, i)
        if dia_semana.weekday() == 6 or dia_semana.weekday() == 5:
            pass
        else:
            dias_mes_1.append(dia_semana)
    return dias_mes_1


def criarFrequencia(mes, sala):
    freq_salas = []
    frequencias = []
    for dia in mes:
        try:
            frequencia = Frequencia.objects.get(sala=sala, data=dia)
            freq_salas.append(frequencia)
        except:
            freq01 = Frequencia(sala=sala, data=dia, presentes=0, total=sala.total_alunos, status=True)
            freq_salas.append(freq01)
            frequencias.append(
                freq01
            )

    Frequencia.objects.bulk_create(frequencias)

    return freq_salas


def criarFrequenciaDiaria(data, alunos):
    freq_alunos_salve = []

    for aluno in alunos:
        if not FrequenciaAluno.objects.filter(aluno=aluno, data=data).exists():
            freq_alunos_salve.append(FrequenciaAluno(aluno=aluno, data=data))

    FrequenciaAluno.objects.bulk_create(freq_alunos_salve, ignore_conflicts=True)



def percentual(frequencias, freq):
    contador = 0
    total = len(frequencias)
    for frequency in frequencias:
        if frequency.presente:
            contador += 1
    resultado = (contador/total) * 100
    freq.presentes = int(resultado)
    freq.save()