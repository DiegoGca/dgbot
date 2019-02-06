#!/usr/bin/python3.6

import re
# import os
# import sys
import logging
import threading
import requests
import datetime

from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import RegexHandler, CallbackQueryHandler
from telegram import ReplyKeyboardRemove
from telegram import ChatAction
from functools import wraps

from credentials import LIST_OF_ADMINS, TOKEN

import telegramcalendar


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='dgbot.log',
                    level=logging.DEBUG)
logging.info('Starting bot...')


# TODO: add decorators external file
# Restricted Decorator
def restricted(func):
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


# /start
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


@send_action(ChatAction.UPLOAD_PHOTO)
def dog_pict(bot, update):
    """Send a doggo pict / gif."""
    url = get_image_url()
    chat_id = update.message.chat_id
    file_extension = re.search("([^.]*)$", url).group(1).lower()
    logging.info('DoggoImageUrl: %s', url)
    if file_extension == 'gif':
        bot.send_animation(chat_id=chat_id, animation=url)
    else:
        bot.send_photo(chat_id=chat_id, photo=url)

    today = datetime.date.today()  # no timezone!
    if chat_id == '211589207' or (today.month == 1 and today.day == 22):
        msg = "Feliz Cumpleaños GGGGGKIKO!!\n aunque 15 dias tarde :/"
        logging.info("KIKO")
        update.message.reply_text(msg)


@send_action(ChatAction.TYPING)
def echo(bot, update):
    """Echo the user message."""  # TODO without /echo
    update.message.reply_text(update.message.text)
    # shortcut to bot.send_message with sane defaults
    # chat_id = update.message.chat_id
    # bot.send_message(chat_id=chat_id, text=update.message.text)


# @send_action(ChatAction.TYPING)
def handl_text(bot, update):
    """Process every text"""
    # update.message.reply_text("Texto generico")


def dg(bot, update):  # TODO fix this
    chat_id = update.message.chat_id
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
def ping(bot, update):
    ms = 'Tienes una latencia de 27ms.\nSe han perdido todos los paquetes que hayan leido esto.'
    update.message.reply_text(ms)


def calendar_handler(bot, update):
    update.message.reply_text("Please select a date: ",
    reply_markup = telegramcalendar.create_calendar())


def inline_handler(bot, update):
    selected, date = telegramcalendar.process_calendar_selection(bot, update)
    if selected:
        bot.send_message(chat_id=update.callback_query.from_user.id,
                        text = "You selected %s"%(date.strftime("%d/%m/%Y")),
                        reply_markup = ReplyKeyboardRemove())


# ----------------------
# otras funciones:

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#advanced-snippets
@restricted
def stop(bot, update):
    threading.Thread(target=shutdown).start()


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, error)


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def get_image_url():
    allowed_extension = ['jpg', 'jpeg', 'png', 'gif']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


# This needs to be run on a new thread because calling 'updater.stop()' inside
# handler (shutdown_cmd) causes a deadlock because it waits for itself to finis
def shutdown():
    updater.stop()
    updater.is_idle = False
# -------------------------


# main
# def main():
updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("calendar", calendar_handler))
dp.add_handler(CallbackQueryHandler(inline_handler))

dp.add_handler(CommandHandler(['dog', 'enrique', 'jj', 'juanju'], dog_pict))
dp.add_handler(CommandHandler('echo',  echo))
dp.add_handler(CommandHandler('stop',  stop))
dp.add_handler(CommandHandler('dg', dg))
dp.add_handler(CommandHandler('ping', ping))

dp.add_handler(RegexHandler('((d|D)+)(((a|A)+)((n|N)+)((i|I))+)', acho))
dp.add_handler(RegexHandler('(.*)(p|P)erd(i|í)(.*)', perdi))
dp.add_handler(RegexHandler('(.*)(d|D)(d|D)(r|R)[0-9](.*)', ddr1))


# on noncommand i.e message - echo the message on Telegram
dp.add_handler(MessageHandler(Filters.text, handl_text))

# log all errors
dp.add_error_handler(error)
updater.start_polling()
updater.idle()

# if __name__ == '__main__':
#     main()
