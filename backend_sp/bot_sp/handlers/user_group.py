from string import punctuation
from aiogram import F, types, Router
import os
from filters.chat_types import ChatTypesFilter


user_group_router = Router()
user_group_router.message.filter(ChatTypesFilter(['group', 'supergroup']))

BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, "restricted_words.txt")

with open(file_path, "r", encoding="utf-8") as f:
    restricted_words = {line.strip().lower() for line in f if line.strip()}

def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


@user_group_router.edited_message()
@user_group_router.message()
async def start_cmd(message: types.Message):
    text = clean_text(message.text.lower())
    world = text.split()

    if restricted_words.intersection(world):
        await message.answer(f"{message.from_user.username},\nОбережно, чат під охороною! Дотримуйтесь порядку 😄")
        await message.delete()