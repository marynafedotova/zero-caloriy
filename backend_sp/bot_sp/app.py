import asyncio
import logging
import os
import sys
import betterlogging as bl

from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # .../backend_sp/bot_sp
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))  # .../backend_sp

sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_sp.settings")

import django
django.setup()


from handlers.user_privat import user_router
from handlers.user_group import user_group_router
from common.bot_cmds_list import private
from middlewares.translations import TgUserManager

def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger =logging.getLogger(__name__)
    logger.info("Starting bot")


load_dotenv()
ALLOWED_UPDETES = ['message', 'edited_message', 'callback_query']
bot = Bot(token=os.getenv("TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

i18n_middleware = I18nMiddleware(core=FluentRuntimeCore(path="locales"), default_locale="uk", manager=TgUserManager(),)




async def main():
    setup_logging()

    i18n_middleware.setup(dp)

    dp.include_router(user_router)
    dp.include_router(user_group_router)

    await bot.delete_webhook(drop_pending_updates=True)
    #await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDETES)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Роботу бота зупинено")
