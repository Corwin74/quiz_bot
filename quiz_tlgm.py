import logging
from random import randint

import redis
from environs import Env
from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from quiz_data_api import load_quiz_data
from tlgm_logger import TlgmLogsHandler

QUESTION, ANSWER = (1, 2)
QUIZ_REPLY = ReplyKeyboardMarkup([['Новый вопрос', 'Сдаться'], ['Мой счет']])
QUIZ_DIR = 'questions'

logger = logging.getLogger(__file__)


def get_new_question(update, context):
    redis = context.bot_data['redis']
    quiz_id = randint(0, context.bot_data['max_quiz_id'])
    redis.set(update.message.chat.id, quiz_id)
    return context.bot_data['quiz'][quiz_id][0]


def start(update, context):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\! Я бот для викторин\!',
        reply_markup=QUIZ_REPLY,
    )
    return QUESTION


def handle_new_question_request(update, context):
    update.message.reply_text(
            get_new_question(update, context),
            reply_markup=QUIZ_REPLY)
    return ANSWER


def handle_solution_attempt(update, context):
    redis = context.bot_data['redis']
    question_id = int(redis.get(update.message.chat.id))
    if update.message.text.lower() == \
            context.bot_data['quiz'][question_id][1]. \
            strip('\"').split('.')[0].lower():
        update.message.reply_text(
            'Правильно! Поздравляю! '
            'Для следующего вопроса нажми «Новый вопрос»',
            reply_markup=QUIZ_REPLY,
        )
        return QUESTION
    update.message.reply_text(
                              'Неправильно… Попробуешь ещё раз?',
                              reply_markup=QUIZ_REPLY
    )
    return ANSWER


def give_up(update, context):
    redis = context.bot_data['redis']
    question_id = int(redis.get(update.message.chat.id))
    update.message.reply_text('Внимание, правильный ответ:\n' +
                              context.bot_data['quiz'][question_id][1],
                              reply_markup=QUIZ_REPLY
                              )
    update.message.reply_text(
        get_new_question(update, context),
        reply_markup=QUIZ_REPLY)
    return ANSWER


def cancel(update, context):
    update.message.reply_text('До следующих встреч!')
    return ConversationHandler.END


def error_handler(update, context):
    logger.exception('Exception', exc_info=context.error)


def main():
    logging.basicConfig(
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.INFO
    )

    redis_db = redis.Redis(
                           charset="utf-8",
                           decode_responses=True
    )

    quiz = load_quiz_data(QUIZ_DIR)

    env = Env()
    env.read_env()
    tlgm_bot_token = env('TLGM_BOT_TOKEN')

    updater = Updater(tlgm_bot_token)
    dispatcher = updater.dispatcher

    dispatcher.bot_data['quiz'] = quiz
    dispatcher.bot_data['max_quiz_id'] = len(quiz) - 1
    dispatcher.bot_data['redis'] = redis_db

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            QUESTION: [
                       MessageHandler(Filters.regex(r'^(Новый вопрос)$'),
                                      handle_new_question_request),
                      ],

            ANSWER: [
                      MessageHandler(Filters.regex(r'^(Сдаться)$'), give_up),
                      MessageHandler(Filters.text & ~Filters.command,
                                     handle_solution_attempt)
                    ],
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
