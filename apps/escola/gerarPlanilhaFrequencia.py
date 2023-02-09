import calendar
import datetime
from calendar import monthrange

from ..aluno.models import Aluno
from ..frequencia.models import Frequencia, FrequenciaAluno
from ..sala.models import Sala


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
            frequencias.append(freq01)

    Frequencia.objects.bulk_create(frequencias)

    return freq_salas


def presentesDia(mes, salas):
    presentes = []
    for dia in mes:
        total = 0
        totalschool = 0
        for sala in salas:
            if Frequencia.objects.filter(sala=sala, data=dia).exists():
                freq = 0
                f = Frequencia.objects.filter(sala=sala, data=dia)
                alunos = Aluno.objects.filter(sala=sala)
                aluno_freq = FrequenciaAluno.objects.filter(data=dia, aluno__in=alunos)
                for frequencia in aluno_freq:
                    if frequencia.presente:
                        freq += 1
                freq_total = f[0].sala.total_alunos
                total += freq
                totalschool += freq_total
        try:
            percentual = ((total / totalschool) * 100)
            presentes.append(int(percentual))
        except:
            print('Impossivel dividir por zero.')

    return presentes


def dias(mes):
    dias01 = []
    for dia in mes:
        dias01.append(dia.strftime('%d'))

    return dias01


def percentual(frequencias, freq):
    contador = 0
    total = len(frequencias)
    for frequency in frequencias:
        if frequency.presente:
            contador += 1
            print(contador)
    resultado = (contador/total) * 100
    freq.presentes = int(resultado)
    freq.save()
