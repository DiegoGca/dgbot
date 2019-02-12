from bs4 import BeautifulSoup
import requests
import re

import datetime

from math import ceil


def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """

    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))


def print_dia(url, datea):  # TODO add other classrooms
    """ imprime el horario de un aula para el
    numero de semana y ndia dados
    :param int nsem: 1-4 numero de la semana dentro del mes
    :param int ndia: numero de dia dentro de la semana
    """

    # print(datea)
    res = datea.day - datea.weekday()
    if res > 0:
        ndia = datea.weekday()
    else:
        ndia = datea.day - 1


    nsem = week_of_month(datea)  # TODO siguiente mes!

    req = requests.get(url)

    try:
        assert req.status_code == 200

        # Pasamos el contenido HTML de la web a un objeto BeautifulSoup()
        html = BeautifulSoup(req.text, "html.parser")

        # Obtener el calendario
        calen = html.find_all('table', {'border': '1'})[0]

        month = calen.find_all('tr')

        ndays = month[nsem].find_all('td', {'style': "font-size:xx-small;"})

        day = ndays[ndia]['onmousedown']   # index out of bounds

        nomostrar = re.search("mostrar\('(.+?)'\)", day).group(1)

        ht_str = BeautifulSoup(nomostrar, "html.parser")

        info = ht_str.find_all('td', {'align': 'LEFT'})

        horario = []
        for a in info:
            if a == info[1]:
                continue  # salatar la fecha
            horario.append(a.text)

        return horario

    except AssertionError:
        print("ERROR: http response code: "+str(req.status_code))


def get_labs_sch(datea):
    # TODO enum de laboratorio [1:hp, 2:sun]
    # Añadir otras aulas
    url = ["http://avellano.usal.es/gesinf/recursos/reservas.jsp?RECURSO=Aula%20Sun",
    "http://avellano.usal.es/gesinf/recursos/reservas.jsp?RECURSO=Laboratorio%20de%20InformAtica",
    "http://avellano.usal.es/gesinf/recursos/reservas.jsp?RECURSO=Laboratorio%20HP"]


    total = ""
    for lab in url:
        result = print_dia(lab, datea)
        pret_result = pretty_lab(result)
        total += pret_result
        total += "\n"
    return total




def pretty_lab(lab):
    """ Prettify json array of lab"""
    # TODO: con o sin fecha?
    sep = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
    prett = sep + "\n" + \
            "<b> " + lab[0].upper() + "</b>\n" + \
            sep + "\n"

    for h in lab:
        if h == lab[0]:
            continue
        # si esta libre: ✅
        if "Libre" in h:
            prett += "✅ "

        elif "Cerrado" in h:
            prett += "🔸 "

        else:
            prett += "🔴 "

        prett += h

        prett += "\n"

    return prett






if __name__ == '__main__':
    import sys
    # url = "http://avellano.usal.es/gesinf/recursos/reservas.jsp?RECURSO=Laboratorio%20HP"
    url = "http://avellano.usal.es/gesinf/recursos/reservas.jsp?RECURSO=Aula%20Sun"
    # url = "http://avellano.usal.es/gesinf/recursos/reservas.jsp?RECURSO=Laboratorio%20de%20InformAtica"
    #print_dia(url, 2, 1)
    """
    result = print_dia(url, int(sys.argv[1]), int(sys.argv[2]))
    for a in result:
        print(a)
    #print_dia(url, 1, 1)
    """

    # tday = datetime.datetime.now()
    #tday = datetime.datetime(2019, 2, int(sys.argv[1]))

    #get_labs_sch(tday)
    aul1 = [
      "Aula Sun",
      "Miercoles 13 de Febrero de 2019",
      "9:00-10:00 Libre",
      "10:00-11:00 Libre",
      "11:00-12:00 Redes de Computadores II. B1",
      "12:00-13:00 Redes de Computadores II. B1",
      "13:00-14:00 Libre",
      "14:00-15:00 Libre",
      "15:00-16:00 Libre",
      "16:00-17:00 Redes de Computadores II. A1",
      "17:00-18:00 Redes de Computadores II. A1",
      "18:00-19:00 Libre",
      "19:00-20:00 Libre",
      "20:00-21:00 Libre"
    ]
    print(pretty_lab(aul1))