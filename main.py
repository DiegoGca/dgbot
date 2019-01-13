#!/usr/bin/python3.6
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests
import re
import sys

from functools import wraps

LIST_OF_ADMINS = [1234, 5678 ]

logging.basicConfig(filename='example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
logging.debug('Starting bot...')



def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url

def get_image_url():
    allowed_extension = ['jpg','jpeg','png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url

def bop(bot, update):
    url = get_image_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)
    
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#advanced-snippets    
@restricted
def stop(bot, update):
    threading.Thread(target=shutdown).start()



# otras funciones:
def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped
    
    
def shutdown():
    updater.stop()
    updater.is_idle = False


# main
def main():
    updater = Updater('API-KEY')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('juanju',bop))
    dp.add_handler(CommandHandler('stop', stop))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
