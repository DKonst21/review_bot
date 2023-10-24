import os
import requests
import telegram
import textwrap

from dotenv import load_dotenv
from time import sleep


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
    # chat_id = os.getenv('CHAT_ID_TG')
    chat_id = '799962439'
    telegram_token = os.getenv('TOKEN_TELEGRAM')
    dewman_token = os.getenv('DWMN_TOKEN')

    last_timestamp = None

    # bot = telegram.Bot(token=telegram_token)
    bot = telegram.Bot(token='6517566984:AAG-8xJpGz7Z1k1Ka-uWH2vABWwPXoZY_tQ')

    while True:
        try:
            url = 'https://dvmn.org/api/long_polling/'
            # headers = {"Authorization": dewman_token}
            headers = {"Authorization": 'afedbb153f6ccb0af553482685e2c18c449190d4'}
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
            bot.send_message(chat_id=chat_id, text='Истекло время ожидания, повторный запрос...')
            continue

        except requests.ConnectionError:
            bot.send_message(chat_id=chat_id, text='Ошибка соединения, повторная попытка через 60 секунд.')
            sleep(60)
            continue


if __name__ == '__main__':
    main()
