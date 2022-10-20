import logging
import time
from random import randint

import redis
import telegram
import vk_api as vk
from environs import Env
from vk_api.exceptions import VkApiError
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkEventType, VkLongPoll

from quiz_data_api import load_quiz_data
from tlgm_logger import TlgmLogsHandler

logger = logging.getLogger(__file__)


def get_quiz_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')
    keyboard.add_line()
    keyboard.add_button('Мой счет')
    return keyboard.get_keyboard()


def main():
    SLEEP_TIME = 10
    START, QUESTION, ANSWER = (1, 2, 3)
    QUIZ_DIR = 'questions'

    env = Env()
    env.read_env()
    vk_api_token = env('VK_API_TOKEN')
    admin_tlgm_chat_id = env('ADMIN_TLGM_CHAT_ID')
    tlgm_bot_token = env('TLGM_BOT_TOKEN')

    redis_db = redis.Redis(
                           charset="utf-8",
                           decode_responses=True
    )
    quiz = load_quiz_data(QUIZ_DIR)
    max_quiz_id = len(quiz) - 1
    tlgm_bot = telegram.Bot(tlgm_bot_token)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        '%H:%M:%S',
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(TlgmLogsHandler(
                                      tlgm_bot,
                                      admin_tlgm_chat_id,
                                      formatter
                                     )
                      )

    vk_session = vk.VkApi(token=vk_api_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info('VK_bot started!')
    state = START
    for event in longpoll.listen():
        try:
            if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
                continue
            if event.text == '/start':
                vk_api.messages.send(
                                    user_id=event.user_id,
                                    message='Привет! Я бот для викторин!',
                                    keyboard=get_quiz_keyboard(),
                                    random_id=randint(1, 1000)
                )
                state = QUESTION
            if event.text == '/cancel':
                vk_api.messages.send(
                                    user_id=event.user_id,
                                    message='До следующих встреч!',
                                    random_id=randint(1, 1000)
                )
                state = START
                continue
            if state == QUESTION and event.text == 'Новый вопрос':
                question_id = randint(0, max_quiz_id)
                redis_db.set(event.user_id, question_id)
                vk_api.messages.send(
                                     user_id=event.user_id,
                                     message=quiz[question_id][0],
                                     keyboard=get_quiz_keyboard(),
                                     random_id=randint(1, 1000)
                )
                state = ANSWER
                continue
            if state == ANSWER and event.text == 'Сдаться':
                question_id = int(redis_db.get(event.user_id))
                vk_api.messages.send(
                        user_id=event.user_id,
                        message=f'Внимание, правильный ответ:\n'
                                f'{quiz[question_id][1]}',
                        random_id=randint(1, 1000)
                )
                question_id = randint(0, max_quiz_id)
                redis_db.set(event.user_id, question_id)
                vk_api.messages.send(
                                    user_id=event.user_id,
                                    message=quiz[question_id][0],
                                    keyboard=get_quiz_keyboard(),
                                    random_id=randint(1, 1000)
                )
                state = ANSWER
                continue
            if state == ANSWER:
                question_id = int(redis_db.get(event.user_id))
                if event.text.lower() == \
                        quiz[question_id][1].strip('\"').split('.')[0].lower():
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message='Правильно! Поздравляю! '
                                'Для следующего вопроса нажми «Новый вопрос»',
                        keyboard=get_quiz_keyboard(),
                        random_id=randint(1, 1000)
                    )
                    state = QUESTION
                    continue
                else:
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message='Неправильно… Попробуешь ещё раз?',
                        keyboard=get_quiz_keyboard(),
                        random_id=randint(1, 1000)
                    )
                    continue
        except VkApiError as exception:
            logger.exception(exception)
            time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
