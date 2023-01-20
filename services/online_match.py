from services import settings
from services import load_href_from_json as load


def main():
    data_dir_absolute = settings.DATA_DIR_ABSOLUTE
    match_id = settings.match_id
    season = settings.season
    round_num = settings.round_num

    online_match_ask_user(match_id, season, round_num, data_dir_absolute)


def online_match_ask_user(m_id, season_year, round_number, data_dir):
    """
    If match status is online ask user if he wants to get online match data.
    :param m_id:
    :param season_year:
    :param round_number:
    :param data_dir:
    """
    while True:
        ask_user_to_get_online_match_stats = input('Do you want to load online data? (y/n): ')
        if ask_user_to_get_online_match_stats == 'y' or ask_user_to_get_online_match_stats == 'yes':
            print(f'Loading online data...')
            break
        elif ask_user_to_get_online_match_stats == 'n' or ask_user_to_get_online_match_stats == 'no':
            load.get_one_match_index_page_from_json(m_id, season_year, round_number, data_dir)
            print(f'Index file of mathc ID {m_id} saved')
            break
        else:
            print('Enter valid answer (yes or no)')
            continue


if __name__ == '__main__':
    main()