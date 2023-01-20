import csv
import json
import re
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

from services import settings


chrome_path = Path('X:/PYTHON/chromedriver_win32.exe')
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
ua = UserAgent()
chrome_options.add_argument(ua.random)
chrome_options.headless = True

driver = webdriver.Chrome(service=Service(chrome_path), options=chrome_options)
browser_test = 'https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html'


def main():
    data_dir_absolute = settings.DATA_DIR_ABSOLUTE
    match_id = settings.match_id
    season = settings.season
    round_num = settings.round_num

    # get_dynamic_number_of_rounds(season)
    # get_dynamic_events_urls(season, round_num, data_dir_absolute)


def get_dynamic_number_of_rounds(season_year: str) -> int:
    """
    Get maximum round number and 'fake' rounds.
    Webpage generates 4 'fake rounds' after maximum regular season round.
    Playoffs 1 round, Final-Four semifinal 1 round, Final-Four Final 1 round.
    :param season_year:
    :return: maximum regular season round + 7 (4 fake rounds, 3 playoffs)
    """
    base_url = settings.BASE_URL
    url = base_url + 'euroleague/game-center/?round=1&season=E' + season_year

    try:
        driver.get(url=url)
        time.sleep(2)

        try:
            # if webpage asks for cookies, click 'OK' button
            driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
            time.sleep(1)
        except Exception as ex:
            pass

        # find in dynamic html number of rounds
        number_of_rounds_find = driver.find_element(By.CLASS_NAME, 'game-center_gameCentreMaxRound__ql0mD').text
        # add 'fake' and playoff rounds
        int_numb_of_rounds = int(re.search('\d+$', number_of_rounds_find).group(0)) + 7

        return int_numb_of_rounds

    except Exception as ex:
        print(ex)


def get_dynamic_events_urls(season_year, round_number, data_dir):
    """
    Pars with parser_elb web page.
    Get a dictionary {'match_id': match_id, 'match_href': match_href}.
    Save it to DATA_DIR in csv and json.
    """
    base_url = settings.BASE_URL
    url = base_url + 'euroleague/game-center/?round=' + round_number + '&season=E' + season_year
    # export filenames csv and json
    filename_csv = data_dir / f'season_{season_year}_round_{round_number}.csv'
    filename_json = data_dir / f'season_{season_year}_round_{round_number}.json'
    # matches URLs list
    match_urls = []

    try:
        driver.get(url=url)
        time.sleep(3)

        try:
            # if webpage asks for cookies, click 'OK' button
            driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
            time.sleep(2)
        except Exception as ex:
            pass

        # find all href
        items_href = driver.find_elements(By.CLASS_NAME, "game-card-view_linkWrap__u3Tea")

        # append dict {'match_id': match_id, 'match_href': match_href} to match_urls list
        for item in items_href:
            match_href = item.get_attribute('href')
            match_id = re.search('([0-9]+/[0-9]+\d?)(/)?$', match_href).group(1).replace('/', '')
            match_urls.append({'match_id': match_id, 'match_href': match_href})
        time.sleep(1)

        # save matches list to csv
        with open(filename_csv, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['match_id', 'match_href']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in match_urls:
                writer.writerow(row)

        # save matches list to json
        with open(filename_json, 'w', newline='', encoding='utf-8') as file:
            json.dump(match_urls, file, indent=4, ensure_ascii=False)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
