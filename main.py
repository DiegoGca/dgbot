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
                    level=logging.DEBUG)
logging.debug('Starting bot...')


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped

# TODO /start


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def get_image_url():
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


def bop(bot, update):
    url = get_image_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)   # TODO vs bot?
    # chat_id = update.message.chat_id
    # bot.send_message(chat_id=chat_id, text=update.message.text)


# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#advanced-snippets
@restricted
def stop(bot, update):
    threading.Thread(target=shutdown).start()


# otras funciones:

# This needs to be run on a new thread because calling 'updater.stop()' inside
# handler (shutdown_cmd) causes a deadlock because it waits for itself to finish
def shutdown():
    updater.stop()
    updater.is_idle = False


# main
# def main():
updater = Updater(TOKEN)
dp = updater.dispatcher
dp.add_handler(CommandHandler('juanju', bop))
dp.add_handler(CommandHandler('stop',  stop))


# on noncommand i.e message - echo the message on Telegram
dp.add_handler(MessageHandler(Filters.text, echo))
updater.start_polling()
updater.idle()

# if __name__ == '__main__':
#     main()
