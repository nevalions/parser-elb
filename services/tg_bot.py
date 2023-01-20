import json
from pathlib import Path

from aiogram import Bot, types
from aiogram.dispatcher import  Dispatcher
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import  executor
from aiogram.types import Message, ReplyKeyboardRemove

from services import load_dynamic_html, check, settings, match
from services.auth_data import tg_token
from services import load_href_from_json as load

# DATA_DIR = Path('data')
DATA_DIR_ABSOLUTE = settings.DATA_DIR_ABSOLUTE

bot = Bot(token=tg_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def main():
    executor.start_polling(dp)

class Form(StatesGroup):
    season = State()
    round = State()

@dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message):
    await Form.season.set()
    await message.reply(f'Hi! Enter a season year\n(from 2000 year to 2022): ')

@dp.message_handler(commands=["cancel"])
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.season)
async def process_season_is_digit(message: types.Message):
    await message.reply('Enter valid number')

@dp.message_handler(lambda message: int(message.text) not in range(2000,2023), state=Form.season)
async def process_season_invalid(message: types.Message):
    await message.reply('Enter valid number')

@dp.message_handler(state=Form.season)
async def enter_round(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['season'] = message.text
        s = data['season']
    print(data)
    await message.answer('Loading...')
    await Form.round.set()
    # show user valid rounds in season
    rounds_in_season = load_dynamic_html.get_dynamic_number_of_rounds(s)
    # webpage generates 4 fake rounds from regular season to playoffs
    fake_rounds = [
        rounds_in_season - 6,
        rounds_in_season - 5,
        rounds_in_season - 4,
        rounds_in_season - 3,
    ]

    await message.reply(
        f'Max number of rounds in Regular Season {s} - {rounds_in_season - 7}\n\n'
        f'Playoffs Best of Five: Round #{rounds_in_season - 2}\n'
        f'Final Four Semifinal: Round #{rounds_in_season - 1}\n'
        f'Final Four Final: Round #{rounds_in_season}\n\n'
        f"DON'T select FAKE rounds {fake_rounds[0]}, {fake_rounds[1]}, {fake_rounds[2]}, {fake_rounds[3]}")
    await message.answer('Enter round')


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.round)
async def process_round_is_digit(message: types.Message):
    await message.reply('Enter valid number')

# TODO add check is max number and not fake
# @dp.message_handler(lambda message: int(message.text) in fake_rounds, state=Form.round)
# async def process_round_is_valid(message: types.Message):
#     await message.reply('Enter valid number')

@dp.message_handler(state=Form.round)
async def enter_round(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['round'] = message.text
        r = data['round']
        m_ids_list_of_round = []

        # check if file already was generated
        check.is_season_json_exist(data['season'], r, DATA_DIR_ABSOLUTE)
        # show user list of matches with IDs to select
        matches_ids = load.get_list_of_matches(data['season'], r, DATA_DIR_ABSOLUTE)
        for m_id in matches_ids:
            m_ids_list_of_round.append(m_id["match_id"])
        print(m_ids_list_of_round)
        for i in m_ids_list_of_round:
            await message.answer(f"Select match ID: {i}")

    print(data)


if __name__ == '__main__':
    main()