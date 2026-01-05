from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram_i18n import I18nContext
from aiogram import types


#Мови
class LanguageCD(CallbackData, prefix="lang"):
    lang: str
 

def languege_kb(i18n: I18nContext):
    kb = InlineKeyboardBuilder()

    kb.button(
        text=i18n.languages.uk(),callback_data=LanguageCD(lang="uk")
    )

    kb.button(
        text=i18n.languages.en(),callback_data=LanguageCD(lang="en")
    )

    kb.button(
        text=i18n.languages.ru(),callback_data=LanguageCD(lang="ru")
    )
    kb.adjust(1)
    return kb.as_markup()


#Товари
class ProductCD(CallbackData, prefix="product"):
    action: str          
    index: int           
    product_id: str


def product_kb(
    index: int,
    product_id: str,
    total: int,
    i18n: I18nContext,
):
    kb = InlineKeyboardBuilder()

    prev_index = (index - 1) % total
    next_index = (index + 1) % total

    kb.button(
        text="◀️",
        callback_data=ProductCD(
            action="prev",
            index=prev_index,
            product_id=str(product_id)
        )
    )

    kb.button(
        text=f"{index + 1} / {total}",
        callback_data=ProductCD(action="ignore", index=index, product_id=str(product_id))
    )

    kb.button(
        text="▶️",
        callback_data=ProductCD(
            action="next",
            index=next_index,
            product_id=str(product_id)
        )
    )

    kb.button(
        text=f"➕ {i18n.get('button-add')}",
        callback_data=ProductCD(
            action="add",
            index=index,
            product_id=str(product_id)

        )
    )


    kb.button(
        text=f"↩️ {i18n.get('button-back')}",
        callback_data=ProductCD(
            action="back",
            index=index,
            product_id=str(product_id)

        )
    )

    kb.button(
        text=f"🛒 {i18n.get('button-cart')}",
        callback_data=ProductCD(
            action="cart",
            index=index,
            product_id=str(product_id)

        )
    )


    kb.adjust(3, 1, 2)
    return kb.as_markup()




#Головне меню
def get_main_menu_kb(i18n: I18nContext, with_back: bool=False) -> ReplyKeyboardBuilder:

    """
        Універсальна клавіатура головного меню
    
        Args:
            i18n: Контекст перекладу
            with_back: Додати кнопку 'Назад' (для вкладених меню)
    """
    builder = ReplyKeyboardBuilder()

    #основні кнопки
    buttons = [
        ("🛍️", "button-products", "menu:products"),
        ("🛒", "button-cart", "menu:cart"),
        ("👤", "button-profile", "menu:profile"),
        ("🍰", "button-for_as", "menu:for_as"),  
        ("🚚", "button-delivery", "menu:delivery"),
        ("💵", "button-pay", "menu:pay"),
        ("❓", "button-help", "menu:help"),
        ("🌍", "button-change_language", "menu:change_lang"),
    ]

    for emoji, key, _ in buttons:
        text = f"{emoji} {i18n.get(key)}"
        builder.button(text=text)

    
    if with_back:
        builder.button(text=f"↩️ {i18n.get('button-back')}")

    builder.adjust(2, 2, 2, 2)  # Остання кнопка окремо

    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


#Текст 
def get_button_texts(i18n: I18nContext) -> dict:
    """Повертає словник з текстами всіх кнопок"""
    return {
        "products": i18n.get("button-products"),
        "cart": i18n.get("button-cart"),
        "profile": i18n.get("button-profile"),
        "for_as": i18n.get("button-for_as"),
        "delivery": i18n.get("button-delivery"),
        "pay": i18n.get("button-pay"),
        "help": i18n.get("button-help"),
        "change_language": i18n.get("button-change_language"),
        "back": i18n.get("button-back")
    }


#Доставка
def get_delivery_kb(i18n: I18nContext):
    builder = InlineKeyboardBuilder()

    builder.button(
        text=i18n.user.text_dlvr_glovo(),
        url = "https://food.bolt.eu/uk-ua/158/p/179408-zero-kaloriy?utm_source=share_provider&utm_medium=product&utm_content=menu_header"
    )

    #TODO інші посилання на агрегаторів

    
    builder.button(
        text=f"↩️ {i18n.get('button-back')}",
        callback_data="back"
    )

    return builder.as_markup()




