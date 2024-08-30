import datetime
import logging
import os

import motor.motor_tornado
# import pymongo

from aiogram.utils.exceptions import BotBlocked, BotKicked, UserDeactivated
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tzlocal import get_localzone

from tasks import set_scheduled_jobs

load_dotenv()

# Main telegram bot configs
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Telegram chats
ADMIN_IDS = tuple(os.getenv("ADMIN_IDS").split(","))
GROUP_ID = int(os.getenv("GROUP_ID"))

# Database
MONGO_URL = os.getenv("MONGO_URL")
# cluster = pymongo.MongoClient(MONGO_URL)
cluster = motor.motor_tornado.MotorClient(MONGO_URL)
collusers = cluster.chatbot.users
collreports = cluster.chatbot.reports
collwikis = cluster.chatbot.wikis
colledits = cluster.chatbot.edits


# Telegam supported types
all_content_types = ["text", "sticker", "photo",
                     "voice", "document", "video", "video_note"]


# Logging
if not os.getenv("DEBUG"):
    formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
    logging.basicConfig(
        filename=f'logs/bot-from-{datetime.datetime.now().date()}.log',
        filemode='w',
        format=formatter,
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.WARNING
    )


# On start polling telegram this function running
async def on_startup(dp):
    scheduler = AsyncIOScheduler(timezone=str(get_localzone()))
    scheduler.start()
    set_scheduled_jobs(scheduler, dp.bot, collwikis, colledits)
    for i in ADMIN_IDS:
        try:
            await dp.bot.send_message(i, "Bot are start!")
        except (BotKicked, BotBlocked, UserDeactivated):
            pass


# On stop polling Telegram, this function running and stopping polling's
async def on_shutdown(dp):
    logging.warning("Shutting down..")
    for i in ADMIN_IDS:
        try:
            await dp.bot.send_message(i, "Bot are shutting down!")
        except (BotKicked, BotBlocked, UserDeactivated):
            pass
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bye!")
