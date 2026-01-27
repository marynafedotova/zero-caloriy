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
        callback_data=MenuCD(action="cart") 
    )


    kb.adjust(3, 1, 2)
    return kb.as_markup()




#Головне меню

class MenuCD(CallbackData, prefix="menu"):
    action: str

def get_main_menu_kb(i18n: I18nContext, with_back: bool = False):
    builder = InlineKeyboardBuilder()


    buttons = [
        ("🛍️", "button-products", "products"),
        ("🛒", "button-cart", "cart"),
        ("👤", "button-profile", "profile"),
        ("🍰", "button-for_as", "for_as"),
        ("🚚", "button-delivery", "delivery"),
        ("💵", "button-pay", "pay"),
        ("❓", "button-help", "help"),
        ("🌍", "button-change_language", "change_lang"),
    ]

    for emoji, key, action in buttons:
        builder.button(
            text=f"{emoji} {i18n.get(key)}",
            callback_data=MenuCD(action=action)
        )

    if with_back:
        builder.button(text=f"↩️ {i18n.get('button-back')}", callback_data="back_to_main")

    builder.adjust(2) # Сітка по 2 кнопки в ряд
    return builder.as_markup()

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


#Кошик
class CartCD(CallbackData, prefix="cart"):
    action: str     
    index: int
    product_id: str


def cart_item_kb(index: int, cart_item, total: int, i18n):
    kb = InlineKeyboardBuilder()

    prev_index = (index - 1) % total
    next_index = (index + 1) % total
 
    kb.button(text="➖", callback_data=CartCD(action="minus", index=index, product_id=str(cart_item.product.id)))
    kb.button(text=f"{cart_item.quantity} шт.", callback_data="ignore")
    kb.button(text="➕", callback_data=CartCD(action="plus", index=index, product_id=str(cart_item.product.id)))


    kb.button(text="◀️", callback_data=CartCD(action="prev", index=prev_index, product_id=str(cart_item.product.id)))
    kb.button(text=f"{index + 1} / {total}", callback_data="ignore")
    kb.button(text="▶️", callback_data=CartCD(action="next", index=next_index, product_id=str(cart_item.product.id)))

   
    kb.button(text="🗑️ Видалити", callback_data=CartCD(action="delete", index=index, product_id=str(cart_item.product.id)))
    kb.button(text="✅ Оформити", callback_data="checkout")
    
    kb.button(
        text=f"🛍️ {i18n.get('button-products')}", callback_data=MenuCD(action="products"))
    kb.button(text=f"↩️ {i18n.get('button-back')}", callback_data=CartCD(action="back", index=index, product_id=str(cart_item.product.id)))

    kb.adjust(3, 3, 2, 2)
    return kb.as_markup()



class CheckoutCD(CallbackData, prefix="checkout"):
    method: str  

def get_checkout_method_kb(i18n: I18nContext):
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"🚚 доставка таксі", 
        callback_data=CheckoutCD(method="delivery")
    )
    builder.button(
        text=f"🏪 самовиніс", 
        callback_data=CheckoutCD(method="pickup")
    )
   
    builder.button(
        text=f"↩️ {i18n.get('button-back')}", 
        callback_data=MenuCD(action="cart")
    )

    builder.adjust(2, 1)
    return builder.as_markup()


class PickupCD(CallbackData, prefix="pickup"):
    location: str  

def get_pickup_locations_kb(i18n: I18nContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="ТРЦ SkyMall", callback_data=PickupCD(location="skymall"))
    builder.button(text="ТРЦ Retroville", callback_data=PickupCD(location="retroville"))
    builder.button(text=f"↩️ {i18n.get('button-back')}", callback_data="checkout")
    builder.adjust(1)
    return builder.as_markup()