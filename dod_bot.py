#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import json
import logging
import os

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)

import dod_bot_config  # my configuration file

TOKEN = dod_bot_config.TOKEN

HELP_MESSAGE = """
Привет, абитуриент!
Я хочу сыграть с тобой в одну игру, в процессе которой ты узнаешь, какие направления существуют в ИКНТ, какие технологии там изучают, и где они потом тебе пригодятся! А если наберёшь достаточно баллов, приходи за наградой к стенду ИКНТ!
"""

with open("tasks.json", encoding='utf-8') as json_file:
    TASKS = json.load(json_file)


# Try to print to standard output and log it instead if stdout is unavailable.
def try_print(text):
    try:
        print(text)
    except:
        logger.info(text)


# Get the dispatcher to register handlers
updater = Updater(TOKEN)
bot = updater.bot
dp = updater.dispatcher

# Enable logging
logging.basicConfig(filename='log.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def save_user(user):
    os.makedirs("users", exist_ok=True)
    with open("users/" + str(user['id']) + ".json", 'w') as file:
        json.dump(user, file)


def load_user(id):
    with open("users/" + str(id) + ".json") as file:
        return json.load(file)


def log_answer(update, answer):
    user = update.message.from_user
    try_print(' >>> ' + user.first_name + ':\t' + update.message.text)
    try_print(' <<< ' + answer + '\n\n')


# Log the message and the answer
def answer_text(update, answer_text):
    log_answer(update, answer_text)
    update.message.reply_text(answer_text)


def answer_photo(update, photo_path):
    log_answer(update, '<image ' + str(photo_path) + ' >')
    update.message.reply_photo(photo=photo_path)


# /start
# Initial message
def start(bot, update):
    help(bot, update)  # send instructions
    user = {
        'id': update.message.from_user.id,
        'username': update.message.from_user.username,
        'first_name': update.message.from_user.first_name,
        'last_name': update.message.from_user.last_name,
        'name': "",
        'email': "",
        'task': -1,
        'score': 0
    }
    save_user(user)
    answer_text(update, 'Для начала представься!')


# /help
def help(bot, update):
    log_answer(update, '<help>')
    update.message.reply_text(HELP_MESSAGE)


def send_question(bot, update, task):
    button_list = [[KeyboardButton(s)] for s in task['a']]

    reply_markup = ReplyKeyboardMarkup(button_list, one_time_keyboard=True)
    bot.send_message(update.message.from_user.id, text=task['q'], reply_markup=reply_markup)
    bot.send_photo(update.message.from_user.id, photo=task['p'])


def check_answer(bot, update, user):
    task = TASKS[user['task']]

    if task['r'] == update.message.text:
        user['score'] = user['score'] + 1
        answer_text(update, "Верно! " + task['c'])
    else:
        answer_text(update, "Нет. " + task['c'])

    user['task'] = user['task'] + 1
    save_user(user)

    if user['task'] < len(TASKS):
        send_question(bot, update, TASKS[user['task']])
    else:
        answer_text(update, "Это было последнее задание!\nТы набрал " + str(
            user['score']) + " баллов. Приходи на стенд ИКНТ, авось чем-нибудь наградим :)")


def message_handler(bot, update):
    user = load_user(update.message.from_user.id)

    if user['name'] == "":
        user['name'] = update.message.text
        save_user(user)
        answer_text(update, "Приятно познакомиться, " + user['name'] + "!")
        answer_text(update, "Теперь напиши свой e-mail. ")
        return

    if user['email'] == "":
        if "@" in update.message.text:
            user['email'] = update.message.text
            answer_text(update, "Отлично, приступим!")
            save_user(user)
        else:
            answer_text(update, "Это не корректный адрес!")
            return

    if user['task'] == -1:
        send_question(bot, update, TASKS[0])
        user['task'] = 0
        save_user(user)
    elif user['task'] < len(TASKS):
        check_answer(bot, update, user)
    else:
        answer_text(update, "У меня больше нет заданий. \n"
                            "Приходи на стенд ИКНТ, если хочешь узнать больше об институте!")


def error(bot, update, error):
    try_print('error')
    logger.warning('Update "%s" caused error "%s"' % (update, error))


dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('help', help))
dp.add_handler(MessageHandler(Filters.text, message_handler))
dp.add_error_handler(error)

# Start the Bot
updater.start_polling()
try_print('Started up.')
updater.idle()
