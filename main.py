import json
from pathlib import Path

from services import match, check, load_dynamic_html, message_print
from services import load_href_from_json as load

DATA_DIR = Path('data')
DATA_DIR_ABSOLUTE = DATA_DIR.absolute()


def main():
    """
    Ask user for season year, round number and match_id to parse from webpage.
    Create json file with parsed match data.
    """
    while True:
        # ask user to enter season year
        season = input('Season (from 2000 year to 2022): ')
        try:
            if 1999 < int(season) < 2023:
                # check is it a valid season (presented on webpage)
                break
            else:
                print('Enter a valid year.')
            continue
        except Exception as ex:
            print('Enter a valid year.')
            continue

    # show user valid rounds in season
    rounds_in_season = load_dynamic_html.get_dynamic_number_of_rounds(season)
    message_print.print_number_of_rounds_full(season, rounds_in_season)

    while True:
        # webpage generates 4 fake rounds from regular season to playoffs
        fake_rounds = [
            rounds_in_season - 6,
            rounds_in_season - 5,
            rounds_in_season - 4,
            rounds_in_season - 3,
        ]

        # ask user to enter round number
        round_num = input('Round: ')
        try:
            # ???print(rounds_in_season)
            # check is it a valid round number
            if 0 < int(round_num) <= rounds_in_season and int(round_num) not in fake_rounds:
                break
            else:
                print('Enter a valid round number.')
        except:
            print('Enter a valid round number.')
            continue

    # check if file already was generated
    check.is_season_json_exist(season, round_num, DATA_DIR_ABSOLUTE)
    # show user list of matches with IDs to select
    load.get_list_of_matches(season, round_num, DATA_DIR_ABSOLUTE)

    # ask user to enter match ID
    match_id = input('Match ID: ')
    # check if match html file already exist
    check.is_match_href_exist(match_id, season, round_num, DATA_DIR_ABSOLUTE)
    # check if match index file is up-to-date and status (planed, online, finished)
    check.is_match_index_file_up_to_date(match_id, season, round_num, DATA_DIR_ABSOLUTE)

    # parse match data from html file
    full_match_data = match.parse_match_index_page(match_id, DATA_DIR_ABSOLUTE)
    print(full_match_data)

    # save parsed data to json file
    full_match_data_file_name = DATA_DIR_ABSOLUTE / f'Match_{match_id}_FULL_DATA.json'
    try:
        with open(full_match_data_file_name, 'w', newline='', encoding='utf-8') as output_file:
            json.dump(full_match_data, output_file, indent=4, ensure_ascii=False)
        print(f'File successfully saved {full_match_data_file_name}')
    except Exception:
        print(Exception)
        print('Error saving file to folder.')


if __name__ == '__main__':
    main()
