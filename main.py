import logging


from aiogram import executor, types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import admin_commands
import configs
import handlers

from configs import BOT_TOKEN, MONGO_URL


class SetReport(StatesGroup):
    report = State()

logging.basicConfig(level=logging.DEBUG)
bot = Bot(BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MongoStorage(uri=MONGO_URL)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await handlers.start_menu_handler(message, bot)
    await bot.send_message(message.from_user.id, "Hello, <b>{user}</b>!".format(user=message.from_user.full_name))


@dp.message_handler(commands='lang')
async def cmd_lang(message: types.Message, locale):
    # print(locale)
    # For setting custom lang you have to modify i18n middleware
    await message.reply('Your current language: <i>{language}</i>'.format(language=locale))


@dp.message_handler(commands=["main"])
async def menu(message: types.Message):
    print("LOW", message)
    await handlers.menu_handler(message)


@dp.message_handler(commands=['post'])
async def post(message: types.Message):
    data = {'type': 'text', 'text': 'text', 'entities': None}
    users = 390736292,
    await admin_commands.send_post_all_users(data, users, bot)


@dp.message_handler(commands=["report"])
async def report(message: types.Message):
    await SetReport.report.set()
    await message.answer("Bizga o'z takliflaringizni yuboring!")


@dp.message_handler(state=SetReport.report,
                    content_types=configs.all_content_types)
async def report_process(message: types.Message, state: FSMContext):
    await handlers.report_process_handler(message, state, bot)


@dp.my_chat_member_handler()
async def some_handler(my_chat_member: types.ChatMemberUpdated):
    print(my_chat_member)


@dp.chat_member_handler()
async def some_handler(chat_member: types.ChatMemberUpdated):
    print("BAOBAB", chat_member)


@dp.message_handler(content_types=configs.all_content_types)
async def some_text(message: types.Message):
    await handlers.some_text_handler(message, bot)


@dp.pre_checkout_query_handler(lambda shipping_query: True)
async def some_pre_checkout_query_handler(shipping_query: types.ShippingQuery):
    print("shipping", shipping_query)


@dp.shipping_query_handler(lambda shipping_query: True)
async def some_shipping_query_handler(shipping_query: types.ShippingQuery):
    print("EEE", shipping_query)


@dp.errors_handler()
async def some_error(baba, error):
    print("error", baba, error)


@dp.callback_query_handler(lambda callback_query: True)
async def some_callback(callback: types.CallbackQuery):
    print(callback)


if __name__ == '__main__':
    executor.start_polling(dp,
                           on_startup=configs.on_startup,
                           on_shutdown=configs.on_shutdown, skip_updates=True)
