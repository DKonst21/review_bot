import os
import requests
import telegram
import textwrap
import logging

from dotenv import load_dotenv
from time import sleep

logger = logging.getLogger('review_bot')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, tg_chat_id):
        super().__init__()

        logging_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -  %(message)s - %(exc_info)s')
        self.setFormatter(fmt=logging_format)

        self.tg_bot = tg_bot
        self.tg_chat_id = tg_chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.tg_chat_id, text=log_entry)


def send_telegram_notification(lesson_title, is_negative, lesson_url, chat_id, bot):
    if not is_negative:
        result_message = "Преподаватель принял работу, можно приступать к следующему уроку!"
    else:
        result_message = "В работе обнаружились ошибки."
    message = textwrap.dedent(f"""
            У вас проверили работу {lesson_title}
            {result_message}
            Ссылка на урок: {lesson_url}
                    """)
    bot.send_message(chat_id=chat_id, text=message)


def main():
    load_dotenv()
    chat_id = os.getenv('CHAT_ID_TG')
    telegram_token = os.getenv('TOKEN_TELEGRAM')
    dewman_token = os.getenv('DWMN_TOKEN')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s -  %(message)s - %(exc_info)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )
    logger.addHandler(TelegramLogsHandler(tg_bot=telegram_token, tg_chat_id=chat_id))

    last_timestamp = None

    bot = telegram.Bot(token=telegram_token)
    logging.info('Бот запущен.')

    while True:
        try:
            url = 'https://dvmn.org/api/long_polling/'
            headers = {"Authorization": dewman_token}
            params = {'timestamp': last_timestamp}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            lesson_reviews = response.json()

            if lesson_reviews['status'] == 'timeout':
                last_timestamp = lesson_reviews['timestamp_to_request']
            else:
                last_timestamp = lesson_reviews['last_attempt_timestamp']
                new_attempts = lesson_reviews['new_attempts']
                for new_attempt in new_attempts:
                    lesson_title = new_attempt['lesson_title']
                    is_negative = new_attempt['is_negative']
                    lesson_url = new_attempt['lesson_url']
                    send_telegram_notification(lesson_title, is_negative, lesson_url, chat_id, bot)

        except requests.exceptions.ReadTimeout:
            logger.info('Истекло время ожидания, повторный запрос...')
            continue

        except requests.ConnectionError:
            logger.info('Ошибка соединения, повторная попытка через 60 секунд.')
            sleep(60)
            continue


if __name__ == '__main__':
    main()
