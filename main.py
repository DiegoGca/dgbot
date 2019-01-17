#!/usr/bin/python3.6

import re
# import os
# import sys
import logging
import threading
import requests

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import wraps

from credentials import LIST_OF_ADMINS, TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='dgbot.log',
                    level=logging.INFO)
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


# /start
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


@send_action(ChatAction.TYPING)
def dog_pict(bot, update):
    """Send a doggo pict / gif."""
    url = get_image_url()
    chat_id = update.message.chat_id
    file_extension = re.search("([^.]*)$", url).group(1).lower()
    if file_extension == 'gif':
        bot.send_animation(chat_id=chat_id, animation=url)
    else:
        bot.send_photo(chat_id=chat_id, photo=url)


@send_action(ChatAction.UPLOAD_PHOTO)
def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)
    # shortcut to bot.send_message with sane defaults
    # chat_id = update.message.chat_id
    # bot.send_message(chat_id=chat_id, text=update.message.text)


# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#advanced-snippets
@restricted
def stop(bot, update):
    threading.Thread(target=shutdown).start()


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


# ----------------------
# otras funciones:
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
dp.add_handler(CommandHandler('juanju', dog_pict))
dp.add_handler(CommandHandler('echo',  echo))
dp.add_handler(CommandHandler('stop',  stop))

# on noncommand i.e message - echo the message on Telegram
dp.add_handler(MessageHandler(Filters.text, echo))

# log all errors
dp.add_error_handler(error)
updater.start_polling()
updater.idle()

# if __name__ == '__main__':
#     main()
