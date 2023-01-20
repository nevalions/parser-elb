import sys

from bs4 import BeautifulSoup

from services import settings


def main():
    data_dir_absolute = settings.DATA_DIR_ABSOLUTE
    match_id = settings.match_id
    season = settings.season
    round_num = settings.round_num

    print(get_rosters_from_html_file(match_id, data_dir_absolute))


def get_rosters_from_html_file(m_id, data_dir):
    match_file = f'{m_id}_index.html'
    file_to_open = data_dir / match_file

    try:
        with open(file_to_open, 'r') as file:
            src = file.read()
    except FileNotFoundError:
        sys.exit(f'There is no file with name: {file_to_open}')

    soup = BeautifulSoup(src, 'lxml')

    match_roster_a = []
    match_roster_b = []
    player = {
        "player_id": "",
        "player_first_name": "",
        "player_second_name": '',
        "number": ''
    }

    roster_a_find_div = soup.find_all('div', {
        'class': 'game-roster-group_teamPlayers__FuDyl game-roster-group_homeTeamPlayers__1KErS'})
    roster_b_find_div = soup.find_all('div', {
        'class': 'game-roster-group_teamPlayers__FuDyl game-roster-group_awayTeamPlayers__uj2Lr'})
    roster_find_first_name_class = {'class': 'game-roster-group-player_playerFirstName__hdckw'}
    roster_find_second_name_class = {'class': 'game-roster-group-player_playerLastName__1F5Ct'}
    roster_find_number_class = {'class': 'game-roster-group-player_playerTshirtNumber__1KPsB'}

    for div in roster_a_find_div:
        for p in div:
            try:
                player['player_id'] = p.get('href').split('/')[-2]
                player['player_first_name'] = p.find('div', roster_find_first_name_class).text.title()
                player['player_second_name'] = p.find('div', roster_find_second_name_class).text.title()
                player['number'] = p.find('span', roster_find_number_class).text
                match_roster_a.append(player.copy())
            except AttributeError:
                if not player['player_id'].isdigit():
                    player['player_id'] = 'coach'
                    player['number'] = '100'
                    match_roster_a.append(player.copy())

    for div in roster_b_find_div:
        for p in div:
            try:
                player['player_id'] = p.get('href').split('/')[-2]
                player['player_first_name'] = p.find('div', roster_find_first_name_class).text.title()
                player['player_second_name'] = p.find('div', roster_find_second_name_class).text.title()
                player['number'] = p.find('span', roster_find_number_class).text
                match_roster_b.append(player.copy())
            except AttributeError:
                if not player['player_id'].isdigit():
                    player['player_id'] = 'coach'
                    player['number'] = '100'
                    match_roster_b.append(player.copy())

    return sorted(match_roster_a, key=lambda n: int(n['number'])), sorted(match_roster_b,
                                                                          key=lambda n: int(n['number']))


if __name__ == "__main__":
    main()
