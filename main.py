#!/usr/bin/python3.6

import re
import os
# import sys
import logging
import threading
import requests
# import datetime


from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, RegexHandler, CallbackQueryHandler)
from telegram import ReplyKeyboardRemove
from telegram import ChatAction
from functools import wraps

# from credentials import LIST_OF_ADMINS, TOKEN
try:
    from credentials import LIST_OF_ADMINS, TOKEN
except ImportError:
    TOKEN = os.getenv('TOKEN')
    # parse environment variable to list:
    strlist = os.getenv('LIST_OF_ADMINS')

    LIST_OF_ADMINS = []
    strlist = strlist.strip('[]')
    strlist = map(str.strip, strlist.split(','))
    for item in strlist:
        LIST_OF_ADMINS.append(item)

import telegramcalendar
import aulas
import teleaula

updater = None

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='dgbot.log',
                    level=logging.DEBUG)
logging.info('Starting bot...')


# TODO: add decorators external file
# TODO: prepare telegram api wrapper v12
# Restricted Decorator
def restricted(func):
    """Restrict the access of a handler to only
    the user_ids specified in LIST_OF_ADMINS
    https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#advanced-snippets
    """
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            logging.warning('Unauthorized access denied for "%s"', user_id)
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(bot, update, **kwargs)
        return command_func

    return decorator

#####################################


# /start
def start(bot, update):  # TODO add more info
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


@send_action(ChatAction.UPLOAD_PHOTO)
def dog_pict(bot, update):
    """Send a doggo pict / gif."""
    url = get_dog_url()
    chat_id = update.message.chat_id
    file_extension = re.search("([^.]*)$", url).group(1).lower()
    logging.info('DoggoImageUrl: %s', url)
    if file_extension == 'gif':
        bot.send_animation(chat_id=chat_id, animation=url)
    else:
        bot.send_photo(chat_id=chat_id, photo=url)


@send_action(ChatAction.UPLOAD_PHOTO)
def cat_pict(bot, update):
    """Send cat pict """
    url = get_cat_url()
    chat_id = update.message.chat_id
    file_extension = re.search("([^.]*)$", url).group(1).lower()
    logging.info('CatImage url: %s', url)
    if file_extension == 'gif':
        bot.send_animation(chat_id=chat_id, animation=url)
    else:
        bot.send_photo(chat_id=chat_id, photo=url)


@send_action(ChatAction.TYPING)
def echo(bot, update, args):
    """Echo the user message."""
    text = ' '.join(args)
    update.message.reply_text(text)
    # shortcut to bot.send_message with sane defaults
    # chat_id = update.message.chat_id
    # bot.send_message(chat_id=chat_id, text=update.message.text)


# @send_action(ChatAction.TYPING)
def handl_text(bot, update):
    """Process every text"""
    # update.message.reply_text("Texto generico")


def dg(bot, update):
    """ BUG: sending these imgs crashes the bot
        TODO: fix
    """
    chat_id = update.message.chat_id
    logging.info('dg: sending imgs')
    bot.send_photo(chat_id=chat_id, photo='https://random.dog/8f04ddb3-2b72-4bd1-8c02-c5ab49ac7292.jpg')
    logging.info('---error:')
    bot.send_photo(chat_id=chat_id, photo='https://random.dog/59f02432-b972-4428-935b-4efb0af83456.jpg')
    bot.send_animation(chat_id=chat_id, animation='https://random.dog/3254832e-ace1-414c-9d66-e4d968f2928f.gif')


@send_action(ChatAction.TYPING)
def acho(bot, update):
    update.message.reply_text("ACHO!")


@send_action(ChatAction.TYPING)
def perdi(bot, update):
    update.message.reply_text("¿El qué?")


@send_action(ChatAction.TYPING)
def ddr1(bot, update):
    update.message.reply_text("¿Alguien tiene DDR1?")


@send_action(ChatAction.TYPING)
def s27(bot, update):
    chat_id = update.message.chat_id
    gif_27 = 'CgADBAADWIMAAtoZZAeHClhlqwXnwQI'  # file_id
    bot.send_animation(chat_id=chat_id, animation=gif_27)


@send_action(ChatAction.TYPING)
def rajao(bot, update):
    chat_id = update.message.chat_id
    gif_raja = 'CgADBAADAgMAAq5J-VMZu-JjpRD2qgI'  # file_id
    bot.send_animation(chat_id=chat_id, animation=gif_raja)


@send_action(ChatAction.TYPING)
def ping(bot, update):
    import time
    time.sleep(1)
    ms = 'Tienes una latencia de 27ms.\nSe han perdido todos los paquetes que hayan leido esto.'
    update.message.reply_text(ms)


def aula(bot, update):
    # TODO: /libres: muestra las aulas LIBRES de un dia, ordenada por más horas
    # o las aulas libres en las siguientes horas
    # TODO aceptar parametro de seleccion de dia
    update.message.reply_text("HORAS DE AULAS: ",
    reply_markup=teleaula.create_table())


@send_action(ChatAction.UPLOAD_PHOTO)
def horario(bot, update):
    """ Send timetable pic """
    bot.send_photo(chat_id=update.message.chat_id,
    photo=open('assets/img_horario4.png', 'rb'))
    # TODO añadir horario por persona


@send_action(ChatAction.UPLOAD_PHOTO)
def mihorario(bot, update):
    """ Send timetable pic """
    bot.send_photo(chat_id=update.message.chat_id,
    photo=open('assets/horario_dg.png', 'rb'))
    # TODO añadir horario por persona


def calendar_handler(bot, update):
    update.message.reply_text("Selecciona una fecha: ",
    reply_markup=telegramcalendar.create_calendar())


def inline_handler(bot, update):
    selected, date = telegramcalendar.process_calendar_selection(bot, update)
    if selected:
        msg = aulas.get_labs_sch(date)
        bot.send_message(chat_id=update.callback_query.message.chat.id,
                        text=msg,
                        parse_mode='HTML',
                        reply_markup=ReplyKeyboardRemove())

###


@restricted
def stop(bot, update):
    """ /stop : Stop the bot and log, as suggested in:
    https://github.com/python-telegram-bot/python-telegram-bot/issues/801#issuecomment-323778248
     """
    ms = 'Se va a detener el bot'
    update.message.reply_text(ms)
    logging.info('Se ha recibido /stop. ' + ms)
    threading.Thread(target=shutdown).start()


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, error)


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def get_dog_url():
    allowed_extension = ['jpg', 'jpeg', 'png', 'gif']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


def get_cat_url():
    contents = requests.get('https://api.thecatapi.com/v1/images/search').json()
    url = contents[0]['url']
    return url


# This needs to be run on a new thread because calling 'updater.stop()' inside
# handler (shutdown_cmd) causes a deadlock because it waits for itself to finis
def shutdown():
    updater.stop()
    updater.is_idle = False
    logging.info('Bot Detenido')
# -------------------------


# main
def main():
    global updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler('echo', echo, pass_args=True))
    dp.add_handler(CommandHandler(['dog', 'jj', 'juanju'], dog_pict))
    dp.add_handler(CommandHandler(['cat', 'gatoperro'], cat_pict))
    dp.add_handler(CommandHandler('stop', stop))
    dp.add_handler(CommandHandler('dg8',  dg))
    dp.add_handler(CommandHandler('ping', ping))
    dp.add_handler(CommandHandler('horario', horario))
    dp.add_handler(CommandHandler('mihorario', mihorario))
    dp.add_handler(CommandHandler('aula', aula))
    dp.add_handler(CommandHandler(["calendar", "calendario"], calendar_handler))
    dp.add_handler(CallbackQueryHandler(inline_handler))

    # Regex:
    p = re.compile('d+a+n+i+', re.IGNORECASE)
    dp.add_handler(RegexHandler(p, acho))

    p = re.compile('(.*)pe+rd(i|í)(.*)', re.IGNORECASE)
    dp.add_handler(RegexHandler(p, perdi))

    p = re.compile('(.*)ddr[0-9](.*)', re.IGNORECASE)
    dp.add_handler(RegexHandler(p, ddr1))

    dp.add_handler(RegexHandler('(.*)27(.*)', s27))

    p = re.compile('(.*)rajao(.*)', re.IGNORECASE)
    dp.add_handler(RegexHandler(p, rajao))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, handl_text))

    # log all errors
    dp.add_error_handler(error)

    # TODO: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#simple-way-of-restarting-the-bot

    # send msg to admin on start
    print(LIST_OF_ADMINS)
    for chat_id in LIST_OF_ADMINS:
        msg = "==============\n"
        msg += " STARTING BOT \n"
        msg += "=============="
        print(chat_id)
        updater.bot.send_message(chat_id=chat_id, text=msg)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
