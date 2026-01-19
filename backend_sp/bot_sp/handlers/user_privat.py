import os
from pathlib import Path
from typing import TYPE_CHECKING
from aiogram import F, types, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, InputMediaPhoto, FSInputFile
from aiogram.filters import CommandStart, or_f
from aiogram_i18n import I18nContext
from aiogram.exceptions import TelegramBadRequest
from asgiref.sync import sync_to_async

from filters.chat_types import ChatTypesFilter

from kbds.kb import get_main_menu_kb, LanguageCD, languege_kb, ProductCD, product_kb, get_delivery_kb
from middlewares.database.request_db import get_product



if TYPE_CHECKING:
    from stub.stub import I18nContext

user_router = Router()
user_router.message.filter(ChatTypesFilter(['private']))


@user_router.message(
    or_f(
        CommandStart(),
        F.text.endswith("Change language"),
        F.text.endswith("Змінити мову"),
        F.text.endswith("Изменить язык"),
    )
)
async def start(message: types.Message, i18n: I18nContext):
    text = i18n.user.start_cmd()
    await message.answer(text, reply_markup=languege_kb(i18n))


@user_router.callback_query(LanguageCD.filter())
async def change_language(callback_query: types.CallbackQuery, callback_data: LanguageCD, i18n: I18nContext):
    await i18n.set_locale(callback_data.lang)


    await callback_query.answer()
    
    await callback_query.message.edit_text(
        text=i18n.user.language_changed()
    )
    
    await callback_query.message.answer(
        text=i18n.user.choose_option(), 
        reply_markup=get_main_menu_kb(i18n)
    )


#Кнопка назад
async def send_main_menu(message: types.Message, i18n: I18nContext):
    """Функція для відправки головного меню з Reply-клавіатурою"""
    await message.answer(i18n.user.choose_option(), reply_markup=get_main_menu_kb(i18n))


#Визначення мови
def get_lang(i18n: I18nContext) -> str:
    if not i18n.set_locale:
        return 'uk'
    return i18n.locale.split("-")[0]


def get_i18n_field(obj, field: str, i18n:I18nContext) -> str:
    lang = get_lang(i18n)
    val = getattr(obj, f"{field}_{lang}", None) or getattr(obj, f"{field}_uk", None)

    if val is None or val == "" or str(val).lower() == "none":
        return "-"
    return str(val)



#Товари
BASE_DIR = Path(__file__).resolve().parent.parent 
NO_IMAGE_PATH = os.path.join(BASE_DIR, "media", "no_image.jpg")

def format_inline_nutrition(additional_info: str) -> str:
    if not additional_info or additional_info == "-":
        return "-"
    parts = []
    for line in additional_info.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            parts.append(f"{key.strip()}: {value.strip()}")
    return " | ".join(parts) if parts else "-"


def product_text(product, i18n) -> str:

    name = get_i18n_field(product, "name", i18n)
    description = get_i18n_field(product, "description", i18n)
    additional_info = get_i18n_field(product, "additional_info", i18n)
    

    nutrition = format_inline_nutrition(additional_info)
    
    price = getattr(product, 'price', 0)
    weight = getattr(product, 'weight', 0)
    

    return (
        f"<b>{name}</b>\n\n"
        f"<b>{i18n.user.product_ingredients()}</b> {description}\n\n"
        f"<b>{i18n.user.product_nutrition()}</b>\n"
        f"{nutrition}\n\n"
        f"💵 {price:.0f} грн / {weight * 1000:.0f} {i18n.user.gram()}"
    )


async def get_safe_media(image_url: str):
    """Визначає, що відправити: посилання чи локальний файл."""
    if image_url and image_url.startswith("http") and any(image_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
        return image_url
    
    if os.path.exists(NO_IMAGE_PATH):
        return FSInputFile(NO_IMAGE_PATH)
    
    return "https://via.placeholder.com/500x500.png?text=No+Image"

@user_router.message(or_f(
    F.text.endswith('Товари'),
    F.text.endswith('Products'),
    F.text.endswith('Товары'),
))
async def show_products(message: Message, i18n):
    products = await get_product()
    if not products:
        await message.answer("Товари відсутні")
        return

    index = 0
    product = products[index]
    
    await message.answer(i18n.user.empty_text(), reply_markup=ReplyKeyboardRemove())

    media = await get_safe_media(product.image_url)
    
    await message.answer_photo(
        photo=media,
        caption=product_text(product, i18n),
        parse_mode="HTML",
        reply_markup=product_kb(index=index, product_id=product.id, total=len(products), i18n=i18n)
    )

@user_router.callback_query(ProductCD.filter())
async def product_actions(callback: CallbackQuery, callback_data: ProductCD, i18n):
    products = await get_product()
    if not products:
        await callback.answer("Товари не знайдено")
        return

    index = callback_data.index % len(products)
    product = products[index]
    action = callback_data.action

    if action in ("prev", "next"):
        media_content = await get_safe_media(product.image_url)
        
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=media_content,
                    caption=product_text(product, i18n),
                    parse_mode="HTML"
                ),
                reply_markup=product_kb(index=index, product_id=product.id, total=len(products), i18n=i18n)
            )
        except TelegramBadRequest as e:
            if "wrong type" in str(e) or "failed to get HTTP" in str(e):
                # РЕЗЕРВНИЙ ВАРІАНТ: Якщо URL битий, примусово шлемо заглушку
                backup_media = FSInputFile(NO_IMAGE_PATH) if os.path.exists(NO_IMAGE_PATH) else "https://via.placeholder.com/500x500.png"
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=backup_media, caption=product_text(product, i18n), parse_mode="HTML"),
                    reply_markup=product_kb(index=index, product_id=product.id, total=len(products), i18n=i18n)
                )
            elif "message is not modified" in str(e):
                pass
        
    elif action == "back":
        await callback.message.delete()
        await callback.message.answer(i18n.user.choose_option(), reply_markup=get_main_menu_kb(i18n))

    elif action == "add":
        await callback.answer(i18n.user.added_to_cart())
        
    await callback.answer()

#Доставка
@user_router.message(
    or_f(
        CommandStart(),
        F.text.endswith("Delivery"),
        F.text.endswith("Доставка"),
        F.text.endswith("Доставка"),
    )
)
async def delivery(message: types.Message, i18n: I18nContext):
    text = i18n.user.choice_dlvr()
    frst_text = f"🚚"
    await message.answer(frst_text, reply_markup=ReplyKeyboardRemove())
    await message.answer(text, reply_markup=get_delivery_kb(i18n))

@user_router.callback_query(F.data == "back")
async def back_callback(callback: types.CallbackQuery, i18n: I18nContext):
    await callback.message.delete()
    await send_main_menu(callback.message, i18n)
    await callback.answer()

