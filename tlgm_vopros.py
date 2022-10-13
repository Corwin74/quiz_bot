import logging
import os
from random import randint

import redis
from environs import Env
from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, Filters, MessageHandler,
                             Updater, ConversationHandler)

from tlgm_logger import TlgmLogsHandler

QUESTION = 1
ANSWER = 2
HINT = 3

logger = logging.getLogger(__file__)


def echo(update, context):
    redis = context.bot_data['redis']
    question_id = int(redis.get(update.message.chat.id))
    print(context.bot_data['quiz'][question_id][1])
    print(update.message.text)



def start(update, context):
    user = update.effective_user
    custom_keyboard = [['Новый вопрос', 'Сдаться'],['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\! Я бот для викторин\!',
        reply_markup=reply_markup,
    )
    return QUESTION

def question(update, context):
    user = update.effective_user
    custom_keyboard = [['Новый вопрос', 'Сдаться'],['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    redis = context.bot_data['redis']
    quiz_id = randint(0, context.bot_data['max_quiz_id'])
    redis.set(update.message.chat.id, quiz_id)
    update.message.reply_text(
            context.bot_data['quiz'][quiz_id][0],
            reply_markup=reply_markup)
    update.message.reply_text(
        context.bot_data['quiz'][quiz_id][1],
        reply_markup=reply_markup)
    return ANSWER

def answer(update, context):
    redis = context.bot_data['redis']
    question_id = int(redis.get(update.message.chat.id))
    if update.message.text.lower() == \
        context.bot_data['quiz'][question_id][1].strip('\"').split('.')[0].lower():
        custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            reply_markup=reply_markup,
        )
        return QUESTION
    update.message.reply_text('Неправильно… Попробуешь ещё раз?')
    return ANSWER

def cancel(update, context):
    update.message.reply_text('Галя, Отмена!')
    return QUESTION

def error_handler(update, context):
    logger.exception('Exception', exc_info=context.error)


def main():
    logging.basicConfig(
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.INFO
    )

    redis_db = redis.Redis(
                           host='localhost',
                           port=6379,
                           db=0,
                           charset="utf-8",
                           decode_responses=True
    )

    files = os.listdir(path='questions')
    quiz = []
    for file in files:
        with open(f'questions/{files[2]}', "r", encoding='KOI8-R') as f:
            content = f.read().rsplit('\n\nВопрос')[1:]
            for paragraph in content:
                chunks = paragraph.split('\n\n')
                quiz.append([" ".join(chunks[0].split("\n")[1:]),
                            " ".join(chunks[1].split("\n")[1:])])

    env = Env()
    env.read_env()
    tlgm_token_bot = env('TLGM_BOT_TOKEN')

    updater = Updater(tlgm_token_bot)
    dispatcher = updater.dispatcher

    dispatcher.bot_data['quiz'] = quiz
    dispatcher.bot_data['max_quiz_id'] = len(quiz) - 1
    dispatcher.bot_data['redis'] = redis_db

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            QUESTION: [
                       MessageHandler(Filters.regex(r'^(Новый вопрос)$'), question),
                       ],

            ANSWER: [
                      MessageHandler(Filters.regex(r'^(Сдаться)$'), cancel),
                      MessageHandler(Filters.text & ~Filters.command, answer)
                    ],
            HINT: []
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )


    dispatcher.add_handler(conv_handler)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        '%H:%M:%S',
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(TlgmLogsHandler(
                                      updater.bot,
                                      env('ADMIN_TLGM_CHAT_ID'),
                                      formatter
                                     )
                      )
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
