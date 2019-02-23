from bs4 import BeautifulSoup
import requests
import re

from math import ceil


def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """

    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))


def get_aula():
    url = "http://campus.usal.es/~aulas/php/infPLibres.php?pre=fc"

    req = requests.get(url)

    try:
        assert req.status_code == 200

        # Pasamos el contenido HTML de la web a un objeto BeautifulSoup()
        html = BeautifulSoup(req.text, "html.parser")

        tabla = html.find_all('table', {'valign': 'MIDDLE'})
        tabladias = tabla[0].find_all('tr')

        dias = []
        for td in tabladias:
            algo = td.find_all('table')
            if algo:
                dias.append(algo)

        result = []
        for d in dias:
            for aul in d:
                if aul == d[8]:
                    break  # eliminar aulas 7 y 8
                horas = aul.find_all('td')
                disp = []
                for h in horas:
                    # <--
                    # TODO eliminar horas (10x8)
                    disp.append(h.text.replace('\xa0', ' '))
                result.append(disp)
            break  # solo el primer dia! TODO select dia

        print(result)
        return result

    except AssertionError:
        print("ERROR: http response code: "+str(req.status_code))


def print_dia(url, datea):
    # TODO add other classrooms
    # + rename (only labs)
    # http://campus.usal.es/~aulas/aulas/fc/fc_pli.htm now working
    # http://campus.usal.es/~aulas/php/infPLibres.php?pre=fc
    """Returns string timetable lab(url) """

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
    get_aula()
