import logging
import random
import time

import telegram
import vk_api as vk
from environs import Env
from vk_api.exceptions import VkApiError
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkEventType, VkLongPoll

from tlgm_logger import TlgmLogsHandler

SLEEP_TIME = 10
START, QUESTION, ANSWER, CANCEL = (1, 2, 3, 4)

logger = logging.getLogger(__file__)

keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Новый вопрос')
keyboard.add_button('Сдаться')
keyboard.add_line()
keyboard.add_button('Мой счет')


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def main():
    env = Env()
    env.read_env()
    vk_api_token = env('VK_API_TOKEN')
    admin_tlgm_chat_id = env('ADMIN_TLGM_CHAT_ID')
    tlgm_bot_token = env('TLGM_BOT_TOKEN')

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
    for event in longpoll.listen():
        try:
            state = START
            if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
                continue
            if state == START and event.text == 'Новый вопрос':
                vk_api.messages.send(
                                     user_id=event.user_id,
                                     message='Куда дел сокровища убиенной тещи?',
                                     keyboard=keyboard.get_keyboard(),
                                     random_id=random.randint(1, 1000)
                )
                state = ANSWER
                continue
            if state == ANSWER and 
            
        except VkApiError as exception:
            logger.exception(exception)
            time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
