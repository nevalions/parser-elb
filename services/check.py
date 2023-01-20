import sys

from datetime import datetime

from services import settings
from services import load_dynamic_html
from services import load_href_from_json as load
from services.match_status import get_match_status_from_json
from services.match_date import get_match_date
from services.online_match import online_match_ask_user
from services.match_status import get_match_status_online


def main():
    data_dir_absolute = settings.DATA_DIR_ABSOLUTE
    match_id = settings.match_id
    season = settings.season
    round_num = settings.round_num

    # is_season_json_exist(season, round_num, data_dir_absolute)
    # is_match_href_exist(match_id, season, round_num, data_dir_absolute)
    # is_max_number_or_fake_round(season, round_num)
    is_match_index_file_up_to_date(match_id, season, round_num, data_dir_absolute)


def is_season_json_exist(season_year, round_number, data_dir):
    """
    Check if season json file with matches IDs and matches URLs exist.
    If not exists, run function to load it (dynamic with parser_elb).
    :param season_year:
    :param round_number:
    :param data_dir:
    """
    match_href_file = f'season_{season_year}_round_{round_number}.json'
    json_file_to_open = data_dir / match_href_file

    if json_file_to_open.is_file():
        print(f'Json file {json_file_to_open} loaded.')

    else:
        print(f'Json file {json_file_to_open} not found.')
        print(f'Trying to download {json_file_to_open}...')
        # if not exist, run function to create file with match ID and match URL
        load_dynamic_html.get_dynamic_events_urls(season_year, round_number, data_dir)


def is_match_index_file_up_to_date(m_id, season_year, round_number, data_dir):
    """
    Check if match index file is up-to-date.
    :param m_id:
    :param season_year:
    :param round_number:
    :param data_dir:
    """
    match_file = f'{m_id}_index.html'
    match_file_to_open = data_dir / match_file

    # get match date and status
    match_date = get_match_date(m_id, data_dir)
    now = datetime.now()
    match_status = get_match_status_from_json(m_id, data_dir)

    if now >= match_date and match_status == 'planed':
        match_status = get_match_status_online(m_id)
        # if match date before now and match status is 'planed'
        # load match index file again
        load.get_one_match_index_page_from_json(m_id, season_year, round_number, data_dir)
        print('File updated.')

    # creation date of match index file
    file_creation_date = datetime.fromtimestamp(match_file_to_open.stat().st_mtime)

    if now >= match_date:
        print('Checking match status...')
        if match_status == 'finished':
            print(f'File is up-to-date and status is "{match_status}"')
        elif match_status == 'online':
            print('Game is online')

            # if match status is online ask user if he wants to get online match data
            online_match_ask_user(m_id, season_year, round_number, data_dir)

    else:
        print('File is up-to-date, no status check.')


def is_match_href_exist(m_id, season_year, round_number, data_dir):
    """
    Check if match index file exist.
    If not exist, load it from URL in json file
    :param m_id:
    :param season_year:
    :param round_number:
    :param data_dir:
    """
    match_file = f'{m_id}_index.html'
    match_file_to_open = data_dir / match_file

    if match_file_to_open.is_file():
        print(f'Index page for match {m_id} found and loaded.')

    else:
        print(f'Index page for match {m_id} not found.')
        print(f'Trying to download {m_id}')
        # If match index not exist, load it from URL in json file
        load.get_one_match_index_page_from_json(m_id, season_year, round_number, data_dir)


def is_max_number_or_fake_round(season_year, round_number):
    """
    Check if entered round number valid. Get maximum round number and 'fake' rounds.
    Webpage generates 4 'fake rounds' after maximum regular season round.
    Playoffs 1 round, Final-Four semifinal 1 round, Final-Four Final 1 round.
    :param season_year:
    :param round_number:
    """
    # get number of rounds from selected season (dynamic with parser_elb)
    rounds_in_season_year = load_dynamic_html.get_dynamic_number_of_rounds(season_year)
    fake_rounds = [
        rounds_in_season_year - 6,
        rounds_in_season_year - 5,
        rounds_in_season_year - 4,
        rounds_in_season_year - 3,
    ]

    if int(round_number) > rounds_in_season_year:
        sys.exit(f'Max {rounds_in_season_year} round in this season.')

    if int(round_number) in fake_rounds:
        sys.exit(f'Selected {round_number} is Faked.')


if __name__ == '__main__':
    main()
