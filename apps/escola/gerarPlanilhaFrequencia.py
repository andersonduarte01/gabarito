import calendar
import datetime
from calendar import monthrange

from ..frequencia.models import Frequencia
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
                f = Frequencia.objects.filter(sala=sala, data=dia)
                freq = f[0].presentes
                freq_total = f[0].total
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

