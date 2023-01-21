import json
import sys

import requests

from fake_useragent import UserAgent
from services import settings

ua = UserAgent()
headers = {'Accept': '*/*', 'user-agent': ua.random}


def main():
    data_dir_absolute = settings.DATA_DIR_ABSOLUTE
    match_id = settings.match_id
    season = settings.season
    round_num = settings.round_num

    # check.is_season_json_exist(season, round_num, data_dir_absolute)
    # get_all_round_matches_index_page_from_json(season, round_num, data_dir_absolute)
    # get_one_match_index_page_from_json(match_id, season, round_num, data_dir_absolute)
    get_list_of_matches(season, round_num, data_dir_absolute)


def matches_index_page_from_json(json_file, data_dir):
    """
    Find urls of matches from parsed file (json).
    Download index pages of matches of selected season and round.
    :param json_file:
    :param data_dir:
    """
    # get matches data from file (matches IDs and matches hrefs)
    with open(json_file, newline='', encoding='utf-8') as file:
        match_href = json.load(file)

    try:
        # download matches index pages
        for match in match_href:
            url = match['match_href']
            req = requests.get(url, headers=headers)
            src = req.text
            file_to_write = data_dir / f'{match["match_id"]}_index.html'
            with open(file_to_write, 'w', newline='', encoding='utf-8') as output_file:
                output_file.write(src)
                print(f'File {file_to_write} added.')
    except KeyError:
        sys.exit(f'No match with this parameters.')


def get_list_of_matches(season_year, round_number, data_dir):
    """
    Get and print list of matches from selected season and round
    :param season_year:
    :param round_number:
    :param data_dir:
    :return list_of_matches: List of matches [{'match_id': match_id, 'match_href': match_href}]
    """
    match_href_file = f'season_{season_year}_round_{round_number}.json'
    json_file_to_open = data_dir / match_href_file
    # returns list of fstrings with available match to select
    m_ids_list = []

    try:
        # load data from season-round json file
        with open(json_file_to_open, 'r') as file:
            list_of_matches = json.load(file)
    except FileNotFoundError:
        sys.exit(f'There is no JSON file with name: {json_file_to_open}')

    for match in list_of_matches:
        m = f'Season {season_year} Round №{round_number} Match ID: {match["match_id"]}'
        m_ids_list.append(m)

    print(*m_ids_list, sep='\n')

    return list_of_matches, m_ids_list


def get_all_round_matches_index_page_from_json(season_year, round_number, data_dir):
    """
    Find urls of matches from parsed file (json).
    Download index pages of matches of selected season and round.
    :param season_year:
    :param round_number:
    :param data_dir:
    :return list_of_matches: List of matches [{'match_id': match_id, 'match_href': match_href}]
    """
    match_href_file = f'season_{season_year}_round_{round_number}.json'
    json_file_to_open = data_dir / match_href_file

    try:
        # get matches data from file (matches IDs and matches hrefs)
        with open(json_file_to_open, 'r') as file:
            list_of_matches = json.load(file)

            # download matches index pages
            for match in list_of_matches:
                url = match['match_href']
                req = requests.get(url, headers=headers)
                src = req.text
                file_to_write = data_dir / f'{match["match_id"]}_index.html'
                with open(file_to_write, 'w', newline='', encoding='utf-8') as output_file:
                    output_file.write(src)
                    print(f'file {file_to_write} added')
    except KeyError:
        sys.exit(f'No match with this parameters.')
    except FileNotFoundError:
        sys.exit(f'There is no JSON file with name: {json_file_to_open}')

    return list_of_matches


def get_one_match_index_page_from_json(m_id, season_year, round_number, data_dir):
    """
    Find url of selected match from parsed file (json).
    Download index page of match by ID of selected season and round.
    :param m_id:
    :param season_year:
    :param round_number:
    :param data_dir:
    :return list_of_matches: List of matches [{'match_id': match_id, 'match_href': match_href}]
    """
    match_href_file = f'season_{season_year}_round_{round_number}.json'
    json_file_to_open = data_dir / match_href_file

    try:
        # get matches data from file (matches IDs and matches hrefs)
        with open(json_file_to_open, 'r') as file:
            list_of_matches = json.load(file)

            for event in list_of_matches:
                try:
                    # get match href by match ID
                    if m_id == event['match_id']:
                        url = event['match_href']
                        req = requests.get(url, headers=headers)
                        src = req.text
                        file_to_write = data_dir / f'{event["match_id"]}_index.html'
                        with open(file_to_write, 'w', newline='', encoding='utf-8') as output_file:
                            output_file.write(src)
                            print(f'File {file_to_write} added.')
                except KeyError:
                    sys.exit(f'No match with this parameters.')

    except FileNotFoundError:
        sys.exit(f'There is no JSON file with name: {json_file_to_open}')

    return list_of_matches


if __name__ == '__main__':
    main()
