import sys

from datetime import datetime
from bs4 import BeautifulSoup

from services import settings, roster
from services.match_status import get_match_status_from_json
from services.match_date import get_match_date


def main():
    data_dir_absolute = settings.DATA_DIR_ABSOLUTE
    match_id = settings.match_id
    season = settings.season
    round_num = settings.round_num

    # get_match_date_time_and_status(match_id, data_dir_absolute)

    # check.is_match_href_exist(match_id, season, round_num, data_dir_absolute)
    match_data = parse_match_index_page(match_id, data_dir_absolute)
    print(match_data)


def parse_match_index_page(m_id, data_dir):
    """
    Parse downloaded match index page.
    Get:
    - match status (planed, online, finished).
    - date and time
    - stadium name
    - home (a)team and away (b)team
    - score (a)team and score (b)team
    - roster (a) team and roster (b)team
    :param m_id:
    :param data_dir:
    :return match_data: List of dict with full match data
    """
    match_data = {
        'matchstatus': '',
        'matchdate': '',
        'matchstadium': '',
        'team_a': '',
        'team_b': '',
        'score_a': '',
        'score_b': '',
        'roster_a': '',
        'roster_b': '',
    }

    match_file = f'{m_id}_index.html'
    match_file_to_open = data_dir / match_file

    try:
        # opem match index file and load html to parse
        with open(match_file_to_open, 'r') as file:
            src_of_match_index = file.read()
    except FileNotFoundError:
        sys.exit(f'There is no file with name: {match_file}')

    # start parser
    soup = BeautifulSoup(src_of_match_index, 'lxml')

    match_data_top = []
    # find <ul> with match data in <li> tags
    for ultag in soup.find_all('ul', {'class': 'event-info_list__1Nrov'}):
        for litag in ultag.find_all('li'):
            match_data_top.append(litag.text)

    match_date_time = get_match_date(m_id, data_dir)
    match_data['matchstatus'] = get_match_status_from_json(m_id, data_dir)
    match_data['matchdate'] = match_date_time.strftime("%d/%m/%Y, %H:%M")
    match_data['matchstadium'] = match_data_top[2]
    match_data['team_a'] = soup.find_all(
        'p', {'class': 'club-info_name__kgCgs'})[0].text.strip()
    match_data['team_b'] = soup.find_all(
        'p', {'class': 'club-info_name__kgCgs'})[1].text.strip()

    # if match is not played, default score is 0:0, because in webpage some ghost info from past match
    if datetime.now() < match_date_time:
        match_data['score_a'] = '0'
        match_data['score_b'] = '0'
    else:
        match_data['score_a'] = soup.find('span', {'aria-label': 'home team score'}).text
        match_data['score_b'] = soup.find('span', {'aria-label': 'away team score'}).text
    match_data['roster_a'], match_data['roster_b'] = roster.get_rosters_from_html_file(m_id, data_dir)

    print('Match data loaded.')

    return match_data


if __name__ == '__main__':
    main()
