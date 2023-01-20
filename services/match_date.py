import sys
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from services import settings


def main():
    data_dir_absolute = settings.DATA_DIR_ABSOLUTE
    match_id = settings.match_id
    season = settings.season
    round_num = settings.round_num

    print(get_match_date(match_id, data_dir_absolute))


def get_match_date(m_id, data_dir) -> datetime:
    """
    Parse and get only match date and time.
    :param m_id:
    :param data_dir:
    :return datetime: Match date and time
    """
    match_file = f'{m_id}_index.html'
    match_file_to_open = data_dir / match_file

    try:
        with open(match_file_to_open, 'r') as file:
            src_of_match_index = file.read()
    except FileNotFoundError:
        sys.exit(f'There is no file with name: {match_file}')

    soup = BeautifulSoup(src_of_match_index, 'lxml')

    for ultag in soup.find_all('ul', {'class': 'event-info_list__1Nrov'}):
        match_date_str = f'{ultag.find_all("li")[1].text} {ultag.find_all("li")[3].text}'
        return datetime.strptime(f'{match_date_str}', '%d %b %Y %H:%M') + timedelta(hours=3)


if __name__ == '__main__':
    main()
