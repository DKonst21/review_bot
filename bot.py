import os
import requests
import telegram
import textwrap

from dotenv import load_dotenv


def send_telegram_notification(lesson_title, is_negative, lesson_url, chat_id, bot):
    if not is_negative:
        result_message = "Преподавателю все понравилось, можно приступать к следущему уроку!"
    else:
        result_message = "К сожалению, в работе нашлись ошибки."
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
    dwmn_token = os.getenv('DWMN_TOKEN')
    dvmn_lp_url = 'https://dvmn.org/api/long_polling/'
    last_timestamp = None
    bot = telegram.Bot(token=telegram_token)
    headers = {'Authorization': f'Token {dwmn_token}'}
    params = {'timestamp': last_timestamp}

    response = requests.get(dvmn_lp_url, headers=headers, params=params)
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


if __name__ == '__main__':
    main()
