import sys
import time
import random

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from services import settings

ua = UserAgent()
headers = {'Accept': '*/*', 'user-agent': ua.random}


def main():
    data_dir_absolute = settings.DATA_DIR_ABSOLUTE
    match_id = settings.match_id
    season = settings.season
    round_num = settings.round_num

    # print(get_match_status_from_json(match_id, data_dir_absolute))
    # print(get_match_status_online(match_id))


def parse_match_index_page_for_status(match_url) -> str:
    """
    Parse webpage html for match status
    :param match_url:
    :return str: Fstring with match status.
    """
    soup = BeautifulSoup(match_url, 'lxml')

    if soup.find('div', {'class': 'game-hero-post_final__1fMME'}):
        if soup.find('div', {'class': 'game-hero-post_final__1fMME'}).text.strip().lower() == 'final':
            return f'finished'

    if soup.find('div', {'class': 'game-duration_container__u6xmJ'}):
        return f'online'

    if soup.find('a', {'class': 'standart-button_btn__pHsqS standart-button__orangeTransparent__2ujRx '
                                'game-hero-pre_buttonLink___tIyO'}):
        if soup.find('a', {'class': 'standart-button_btn__pHsqS standart-button__orangeTransparent__2ujRx '
                                    'game-hero-pre_buttonLink___tIyO'}).text.strip().lower() == 'buy tickets':
            return f'planed'


def get_match_status_from_json(m_id: str, data_dir) -> str:
    """
    Parse and get only match status.
    (planed, online, finished)
    :param m_id:
    :param data_dir:
    :return str: Fstring with match status.
    """
    match_file = f'{m_id}_index.html'
    match_file_to_open = data_dir / match_file

    try:
        with open(match_file_to_open, 'r') as file:
            src_of_match_index = file.read()
    except FileNotFoundError:
        sys.exit(f'There is no file with name: {match_file}')

    return parse_match_index_page_for_status(src_of_match_index)


def get_match_status_online(m_id) -> str:
    """
    Parse match webpage and return fstring with match status.
    (planed, online, finished)
    :param m_id:
    :return:
    """
    season_to_url, match_id_to_url = m_id.strip()[:4], m_id.strip()[4:]
    base_url = settings.BASE_URL
    url = base_url + 'euroleague/game-center/1/txt/E' + season_to_url + '/' + match_id_to_url
    # when you get url first time it shows empty webpage
    print('Trying to get match status online...')
    requests.get(url, headers=headers)
    time.sleep(random.uniform(0.4, 1.2))
    # problem solved by get url second time in one function. Maybe there is more beautiful solution?
    req2 = requests.get(url, headers=headers)
    src = req2.text

    return parse_match_index_page_for_status(src)


if __name__ == '__main__':
    main()
