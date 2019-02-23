from telegram import InlineKeyboardButton, InlineKeyboardMarkup, \
 ReplyKeyboardRemove
import aulas


def create_table():
    """ A partir de una lista de listas con las X horas libres
    crea una tabla de botones en telegram
    """
    # print(schdl)
    # quedarse solo con un dia!!
    # hacer la traspuesta

    # Añadir a la tabla de botones

    schdl = aulas.get_aula()

    keyboard = []
    for aula in schdl:
        # print(aula)
        row = []
        for h in aula:
            row.append(InlineKeyboardButton(h, callback_data='1'))
            # print(h)
        print("====")
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


if __name__ == '__main__':
    create_table()
