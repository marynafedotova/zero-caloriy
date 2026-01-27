import os
from pathlib import Path
from typing import TYPE_CHECKING
from aiogram import F, types, Router, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, InputMediaPhoto, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, or_f
from aiogram_i18n import I18nContext
from aiogram.exceptions import TelegramBadRequest
from asgiref.sync import sync_to_async

from filters.chat_types import ChatTypesFilter

from kbds.kb import get_main_menu_kb, LanguageCD, languege_kb, ProductCD, product_kb, get_delivery_kb, CartCD, cart_item_kb, MenuCD, CheckoutCD, get_checkout_method_kb, PickupCD, get_pickup_locations_kb
from middlewares.database.request_db import get_product, add_to_cart_from_bot, change_cart_quantity, delete_cart_item, get_user_cart_details, save_user_data, clear_user_cart



if TYPE_CHECKING:
    from stub.stub import I18nContext

user_router = Router()
user_router.message.filter(ChatTypesFilter(['private']))


@user_router.message(CommandStart())
async def start(message: types.Message, i18n: I18nContext):
    await message.answer(
        text=f"{i18n.user.start_cmd()}\n\n", 
        reply_markup=languege_kb(i18n)
    )
    try:
        await message.delete()
    except:
        pass



async def send_main_menu(message: types.Message, i18n: I18nContext):
    
    text = i18n.user.choose_option()
    kb = get_main_menu_kb(i18n)

    if message.photo or message.caption:
        await message.delete()
        await message.answer(text=text, reply_markup=kb)
    else:
        try:
            await message.edit_text(text=text, reply_markup=kb)
        except:
            await message.answer(text=text, reply_markup=kb)


@user_router.callback_query(LanguageCD.filter())
async def change_language(callback: types.CallbackQuery, callback_data: LanguageCD, i18n: I18nContext):
  
    await i18n.set_locale(callback_data.lang)
    await callback.answer() 
    
    welcome_text = (
        "<b>Zero Kaloriy — насолоджуйся солодким без провини! 🍰</b>\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "<i>Ми готуємо десерти, які не шкодять вашій фігурі.\n"
        "Оберіть потрібний розділ у меню нижче:</i>"
    )


    sent_message = await callback.message.answer(
        text=welcome_text

    )
  
    try:
        await callback.message.delete()
    except:
        pass

    
    await callback.message.answer(
        text=i18n.user.choose_option(), 
        reply_markup=get_main_menu_kb(i18n)
    )


@user_router.callback_query(MenuCD.filter(F.action == "change_lang"))
async def change_lang_menu_handler(callback: types.CallbackQuery, i18n: I18nContext):
    try:
        await callback.message.delete()
    except:
        pass
        
    await callback.message.answer(
        text=i18n.user.start_cmd(), 
        reply_markup=languege_kb(i18n)
    )
    await callback.answer()

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


@user_router.callback_query(MenuCD.filter(F.action == "products"))
async def show_products_callback(callback: CallbackQuery, callback_data: MenuCD, i18n: I18nContext):
    products = await get_product()
    if not products:
        await callback.answer("Товари відсутні", show_alert=True)
        return

    index = 0
    product = products[index]
    media = await get_safe_media(product.image_url)
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer_photo(
        photo=media,
        caption=product_text(product, i18n),
        parse_mode="HTML",
        reply_markup=product_kb(index=index, product_id=str(product.id), total=len(products), i18n=i18n)
    )
    await callback.answer()

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
        await add_to_cart_from_bot(
            chat_id=callback.message.chat.id,
            product_id=callback_data.product_id

        )
        await callback.answer(i18n.user.added_to_cart())
        
    await callback.answer()



#Кошик
async def render_cart_interface(message: Message, chat_id: int, index: int, i18n):

    cart_items, total_price, total_quantity = await get_user_cart_details(chat_id)

    if not cart_items:
        empty_text = "🛒 Ваш кошик порожній"
        try:
            await message.edit_text(empty_text, reply_markup=None)
        except:
            await message.answer(empty_text)
        return


    if index >= len(cart_items):
        index = 0

    current_item = cart_items[index]
    

    text = (
        f"<b>Товар {index + 1}/{len(cart_items)}</b>\n\n"
        f"<b>{current_item.product.name}</b>\n"
        f"<b>{current_item.product.price} грн</b> × {current_item.quantity} шт\n\n"
        f"💵 <b>Сума:</b> {current_item.product_prace()} грн\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Всього товарів:</b> {total_quantity} шт\n"
        f"💰 <b>До оплати:</b> {total_price} грн"
    )


    kb = cart_item_kb(index, current_item, len(cart_items), i18n)

    try:
        await message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    except:
        await message.answer(text=text, reply_markup=kb, parse_mode="HTML")


@user_router.callback_query(MenuCD.filter(F.action == "cart"))
async def cart_menu_callback(callback: CallbackQuery, i18n: I18nContext):

    try:
        await callback.message.delete()
    except:
        pass

    await render_cart_interface(
        message=callback.message, 
        chat_id=callback.from_user.id, 
        index=0, 
        i18n=i18n
    )
    await callback.answer()


@user_router.callback_query(CartCD.filter())
async def cart_actions(callback: CallbackQuery, callback_data: CartCD, i18n):
    action = callback_data.action
    index = callback_data.index
    product_id = callback_data.product_id
    chat_id = callback.from_user.id

    if action == "plus":
        await change_cart_quantity(chat_id, product_id, 1)
        
    elif action == "minus":
        await change_cart_quantity(chat_id, product_id, -1)
        
    elif action == "delete":
        await delete_cart_item(chat_id, product_id)
        index = 0  
    
    elif action == "back":
        await callback.message.delete()
        await callback.message.answer(
            text=i18n.user.choose_option(), 
            reply_markup=get_main_menu_kb(i18n)
        )
        await callback.answer()
        return  
    
    await render_cart_interface(
        message=callback.message, 
        chat_id=chat_id, 
        index=index, 
        i18n=i18n
    )
    await callback.answer()


#Доставка
@user_router.callback_query(MenuCD.filter(F.action == "delivery"))
async def delivery_callback(callback: CallbackQuery, i18n: I18nContext):
    await callback.message.edit_text(
        text=i18n.user.choice_dlvr(),
        reply_markup=get_delivery_kb(i18n)
    )
    await callback.answer()

@user_router.callback_query(F.data == "back")
async def back_callback(callback: types.CallbackQuery, i18n: I18nContext):
    await callback.message.delete()
    await send_main_menu(callback.message, i18n)
    await callback.answer()


# Оформлення
class OrderPickup(StatesGroup):
    waiting_for_location = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_time = State()

@user_router.callback_query(F.data == "checkout")
async def process_checkout(callback: CallbackQuery, i18n: I18nContext):

    
    await callback.message.edit_text(
        text="Оберіть спосіб отримання замовлення:", 
        reply_markup=get_checkout_method_kb(i18n)
    )
    await callback.answer()


@user_router.callback_query(CheckoutCD.filter())
async def delivery_method_chosen(callback: CallbackQuery, callback_data: CheckoutCD, state: FSMContext, i18n: I18nContext):
    method = callback_data.method
    
    if method == "delivery":
        # Тут можна додати state для доставки в майбутньому
        await callback.message.edit_text(
            text="Ви обрали доставку. Будь ласка, введіть вашу адресу:",
            reply_markup=None 
        )
        
    elif method == "pickup":
        # 1. Встановлюємо стан вибору локації
        await state.set_state(OrderPickup.waiting_for_location)
        
        # 2. Редагуємо повідомлення, показуючи клавіатуру з вибором ТРЦ
        await callback.message.edit_text(
            text="Оберіть точку видачі (самовивіз):",
            reply_markup=get_pickup_locations_kb(i18n) 
        )
    
    await callback.answer()



@user_router.callback_query(OrderPickup.waiting_for_location, PickupCD.filter())
async def pickup_location_chosen(callback: CallbackQuery, callback_data: PickupCD, state: FSMContext):
    await state.update_data(location=callback_data.location)
    await state.set_state(OrderPickup.waiting_for_name)
    await callback.message.edit_text("Введіть ваше ім'я та прізвище:")


@user_router.message(OrderPickup.waiting_for_name)
async def pickup_name_chosen(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderPickup.waiting_for_phone)
    await message.answer("Введіть ваш номер телефону:")
    


@user_router.message(OrderPickup.waiting_for_phone)
async def pickup_phone_chosen(message: Message, state: FSMContext):

    await state.update_data(phone=message.text)
    

    await state.set_state(OrderPickup.waiting_for_time)
    
    await message.answer("О котрій годині ви плануєте зайти за замовленням?")


@user_router.message(OrderPickup.waiting_for_time)
async def pickup_finish(message: Message, state: FSMContext, i18n: I18nContext, bot: Bot):
    await state.update_data(pickup_time=message.text)
    user_data = await state.get_data()
    chat_id = message.from_user.id


    await save_user_data(
        user_id=chat_id,
        name=user_data.get('name'),
        phone=user_data.get('phone')
    )


    cart_items, total_price, total_quantity = await get_user_cart_details(chat_id)
    
    if not cart_items:
        await message.answer("Кошик порожній.")
        await state.clear()
        return

    topics = {"skymall": 2, "retroville": 4}
    location_names = {"skymall": "ТРЦ SkyMall", "retroville": "ТРЦ Retroville"}
    
    target_topic = topics.get(user_data['location'])
    display_location = location_names.get(user_data['location'], "Не вказано")

    items_text = "".join([
        f"• {item.product.name} — <b>{item.quantity} шт.</b> ({item.product.price * item.quantity} грн)\n"
        for item in cart_items
    ])

    admin_message = (
        f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ САМОВИНОСУ(BOT)</b>\n\n"
        f"👤 <b>Клієнт:</b> {user_data['name']}\n"
        f"📞 <b>Телефон:</b> {user_data['phone']}\n"
        f"⏰ <b>Заберу замовлення:</b> {user_data['pickup_time']}\n"
        f"📍 <b>Локація:</b> {display_location}\n\n"
        f"📦 <b>Товари:</b>\n{items_text}\n"
        f"💰 <b>РАЗОМ: {total_price} грн</b>"
    )

    ADMIN_CHAT_ID = os.getenv('CHAT_ID') 
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_message,
        message_thread_id=target_topic,
        parse_mode="HTML"
    )

    await clear_user_cart(chat_id)

    await message.answer(
        f"✅ Дякуємо, {user_data['name']}! Ваше замовлення прийнято.\n"
        f"Чекаємо на вас о {user_data['pickup_time']} у {display_location}.",
        reply_markup=get_main_menu_kb(i18n)
    )
    
    await state.clear()

