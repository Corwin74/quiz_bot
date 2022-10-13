import os
import logging
from random import choice
from environs import Env

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from tlgm_logger import TlgmLogsHandler


logger = logging.getLogger(__file__)


def echo(update, context):
    if update.message.text == 'Новый вопрос':
        update.message.reply_text(choice(context.bot_data['quiz'])[0])


def start(update, context):
    user = update.effective_user
    custom_keyboard = [['Новый вопрос', 'Сдаться'],['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\! Я бот для викторин\!',
        reply_markup=reply_markup,
    )


def error_handler(update, context):
    logger.exception('Exception', exc_info=context.error)


def main():
    logging.basicConfig(
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.INFO
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

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, echo))

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
