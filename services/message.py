def print_number_of_rounds_full(season_year, rounds_in_season_year):
    """
    Print message to user what round numbers are valid in selected season.
    :param season_year:
    :param rounds_in_season_year:
    :return:
    """
    fake_rounds = [
        rounds_in_season_year - 6,
        rounds_in_season_year - 5,
        rounds_in_season_year - 4,
        rounds_in_season_year - 3,
    ]
    print(f'Max number of rounds in Regular Season {season_year} - {rounds_in_season_year - 7}')
    print(f'Playoffs Best of Five: Round #{rounds_in_season_year - 2}')
    print(f'Final Four Semifinal: Round #{rounds_in_season_year - 1}')
    print(f'Final Four Final: Round #{rounds_in_season_year}')
    print(f"DON'T select FAKE rounds {fake_rounds[0]}, {fake_rounds[1]}, {fake_rounds[2]}, {fake_rounds[3]}")