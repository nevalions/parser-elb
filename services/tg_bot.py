import json

from aiogram import Bot, types
from aiogram.dispatcher import  Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import  executor



from services import load_dynamic_html, check, settings, match
from services.auth_data import tg_token
from services import load_href_from_json as load

DATA_DIR_ABSOLUTE = settings.DATA_DIR_ABSOLUTE

bot = Bot(token=tg_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def main():
    executor.start_polling(dp)

class Form(StatesGroup):
    enter_season = State()
    enter_round = State()
    enter_match_id_of_round = State()
    send_match_data_file = State()

@dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message):
    """
    Telegram bot with aiogram, asks user season, round, match to get data.
    It also makes all main checks: ares user messages are valid, if files are generated etc.
    Finally, it can send file to telegram chat.
    """
    await Form.enter_season.set()
    # enter season year
    await message.answer(f'Hi! Enter a season year\n(from 2000 year to 2022): ')

@dp.message_handler(state=Form.enter_season)
async def process_season_is_valid(message: types.Message, state: FSMContext):
    # checks is season year valid
    try:
        if int(message.text) not in range(2000, 2023):
            return await message.reply('Enter a valid season year')
    except Exception as ex:
        print(ex)
        return await message.reply('Enter a valid season year')
    # save season year to memory
    async with state.proxy() as data:
        data['season'] = message.text

    await message.answer('Loading...')
    # show user valid rounds in season
    rounds_in_season = load_dynamic_html.get_dynamic_number_of_rounds(data['season'])
    # webpage generates 4 fake rounds from regular season to playoffs
    fake_rounds = [
        rounds_in_season - 6,
        rounds_in_season - 5,
        rounds_in_season - 4,
        rounds_in_season - 3,
    ]

    await message.answer(
        f'Max number of rounds in Regular Season {data["season"]} - {rounds_in_season - 7}\n\n'
        f'Playoffs Best of Five: Round #{rounds_in_season - 2}\n'
        f'Final Four Semifinal: Round #{rounds_in_season - 1}\n'
        f'Final Four Final: Round #{rounds_in_season}\n\n'
        f"DON'T select FAKE rounds {fake_rounds[0]}, {fake_rounds[1]}, {fake_rounds[2]}, {fake_rounds[3]}")
    # save max round and fake rounds for next checks
    async with state.proxy() as data:
        data['max_rounds'] = rounds_in_season
        data['fake_rounds'] = fake_rounds
    # enter round number
    await Form.enter_round.set()
    await message.answer('Enter round number from list')

@dp.message_handler(state=Form.enter_round)
async def process_round_is_digit(message: types.Message, state: FSMContext):
    # checks is round number valid
    async with state.proxy() as data:
        try:
            if int(message.text) > data['max_rounds'] or int(message.text) in data['fake_rounds']:
                return await message.reply('Enter a valid round number')
        except Exception as ex:
            print(ex)
            return await message.reply('Enter a valid round number')
        data['round'] = message.text

    # check if file already was generated
    check.is_season_json_exist(data['season'], data['round'], DATA_DIR_ABSOLUTE)
    # show user list of matches with IDs to select
    m_ids_fstring_list = load.get_list_of_matches(data['season'], data['round'], DATA_DIR_ABSOLUTE)[2]
    # save ids list, for next step, to select valid match
    async with state.proxy() as data:
        data['list_ids'] = load.get_list_of_matches(data['season'], data['round'], DATA_DIR_ABSOLUTE)[1]
    # print user full list of matches
    await message.answer('\n'.join(map(str, m_ids_fstring_list)))

    await Form.enter_match_id_of_round.set()
    await message.answer('Enter match ID from list')


@dp.message_handler(state=Form.enter_match_id_of_round)
async def process_round_is_valid(message: types.Message, state: FSMContext):
    # checks is match ID in this round
    async with state.proxy() as data:
        try:
            if message.text not in data['list_ids']:
                return await message.reply('Enter a valid match id from list')
        except Exception as ex:
            print(ex)
            return await message.reply('Enter a valid match id from list')
        data['m_id'] = message.text
        print(data)

    await message.answer('Loading...')
    # check if match html file already exist
    check.is_match_href_exist(data['m_id'], data['season'], data['round'], DATA_DIR_ABSOLUTE)
    # check if match index file is up-to-date and status (planed, online, finished)
    check.is_match_index_file_up_to_date(data['m_id'], data['season'], data['round'], DATA_DIR_ABSOLUTE)

    # parse match data from html file
    full_match_data = match.parse_match_index_page(data['m_id'], DATA_DIR_ABSOLUTE)
    # await message.answer(full_match_data)

    full_match_data_file_name = DATA_DIR_ABSOLUTE / f'Match_{data["m_id"]}_FULL_DATA.json'
    try:
        with open(full_match_data_file_name, 'w', newline='', encoding='utf-8') as output_file:
            json.dump(full_match_data, output_file, indent=4, ensure_ascii=False)
        print(f'File successfully saved {full_match_data_file_name}')
        await message.answer(full_match_data_file_name)
    except Exception as ex:
        print(ex)
        print('Error saving file to folder.')

    #send file to user in telegram
    await Form.send_match_data_file.set()
    await message.answer('Do you want to get file in chat? (y/n)')

@dp.message_handler(state=Form.send_match_data_file)
async def process_round_is_valid(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        full_match_data_file_name = DATA_DIR_ABSOLUTE / f'Match_{data["m_id"]}_FULL_DATA.json'
        print(full_match_data_file_name)
        try:
            if message.text in ['yes', 'y']:
                print('sending file')
                await message.answer_document(open(full_match_data_file_name))
                await state.finish()
            elif message.text in ['no', 'n']:
                print('URL to download')
                await state.finish()
            else:
                return await message.reply('Enter a valid answer (y/n)')
        except Exception as ex:
            print(ex)
            return await message.reply('Something goes wrong')

#TODO make some text design

if __name__ == '__main__':
    main()