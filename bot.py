import os
import requests

from dotenv import load_dotenv


def main():
    load_dotenv()
    dwmn_token = os.getenv('DWMN_TOKEN')
    dvmn_lp_url = 'https://dvmn.org/api/user_reviews/'
    last_timestamp = None
    print(dwmn_token, type(dwmn_token))
    headers = {'Authorization': f'Token {dwmn_token}'}
    print(headers)
    params = {'timestamp': last_timestamp}

    response = requests.get(dvmn_lp_url, headers=headers, params=params)
    response.raise_for_status()
    lesson_reviews = response.json()

    print(lesson_reviews)


if __name__ == '__main__':
    main()
