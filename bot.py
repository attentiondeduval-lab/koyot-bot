import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ============================================
#  ШАГ 1: ВСТАВЬ СВОЙ ТОКЕН СЮДА
# ============================================
TOKEN = "8605749499:AAGBfqpuaLuX-EtfXf_HQMsd2ZIQp-n8Ar4"

# ============================================
#  ШАГ 2: ВСТАВЬ ССЫЛКИ НА ФОТО
#  Как получить ссылку:
#  1. Зайди на imgbb.com
#  2. Загрузи фото
#  3. Скопируй "Direct link" и вставь сюда
# ============================================

PHOTOS = {
    "sunrise":      "https://i.ibb.co/h1t1825t/image.jpg",
    "coyote":       "https://i.ibb.co/cXMZ8c1G/IMG-5922.jpg",
    "bigjo":        "https://i.ibb.co/ZpNMn232/IMG-5924.jpg",
    "cheeseroll":  "https://i.ibb.co/xqrfCgyT/IMG-5928.jpg",
    "hamroll":     "https://i.ibb.co/1tpQvF50/IMG-5927.jpg",
    "toastham":    "https://i.ibb.co/R4H99131/IMG-5926.jpg",
    "toastchick":  "https://i.ibb.co/twGZv8kb/IMG-5925.jpg",
}

# ============================================
#  МЕНЮ — структура бота
# ============================================

MENU = {
    # -------- БІГ МЕНЮ --------
    "big_lavash": [
        {
            "id": "sunrise",
            "name": "Санрайс Курячий",
            "price": 330,
            "desc": "Лаваш, салат з капусти, маринований огірок, помідор, курячий стейк, картопля фрі, сир, бринза, соус.",
            "photo": PHOTOS["sunrise"],
        },
        {
            "id": "coyote",
            "name": "Загнаний Койот",
            "price": 350,
            "desc": "Лаваш, тушена цибуля, гриби, свинні сосиски, бекон, перець Чилі, картопля фрі, сир, бринза, соуси.",
            "photo": PHOTOS["coyote"],
        },
    ],
    "big_bulka": [
        {
            "id": "bigjo",
            "name": "Біг-Джо",
            "price": 360,
            "desc": "Чіабата, сир, бринза, дві котлети, бекон, салат Біонда, рукола, свіжі томати, мариновані огірки, маринована цибуля, соус.",
            "photo": PHOTOS["bigjo"],
        },
    ],
    # -------- СЕРЕДНЄ МЕНЮ --------
    "mid_lavash": [
        {
            "id": "cheeseroll",
            "name": "Сендвіч-Cheese-рол",
            "price": 250,
            "desc": "Лаваш, куряче філе, подвійний сир, помідор, салат Біонда, сирний соус.",
            "photo": PHOTOS["cheeseroll"],
        },
        {
            "id": "hamroll",
            "name": "Сендвіч-рол з шинкою",
            "price": 230,
            "desc": "Лаваш, сир, бринза, свинна шинка, гриби, помідор, салат, капуста, соус.",
            "photo": PHOTOS["hamroll"],
        },
    ],
    "mid_bulka": [
        {
            "id": "toastchick",
            "name": "Тост з куркою",
            "price": 255,
            "desc": "Чіабата, соуси, сир, бринза, мариновані гриби, куряче філе.",
            "photo": PHOTOS["toastchick"],
        },
        {
            "id": "toastham",
            "name": "Тост з шинкою",
            "price": 255,
            "desc": "Чіабата, соус, сир, бринза, мариновані гриби, свинна шинка.",
            "photo": PHOTOS["toastham"],
        },
    ],
}

# Словарь для быстрого поиска блюда по id
ALL_ITEMS = {}
for items in MENU.values():
    for item in items:
        ALL_ITEMS[item["id"]] = item

# ============================================
#  КОД БОТА — ничего не меняй ниже
# ============================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


def size_question_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔴 Великий розмір — БІГ МЕНЮ", callback_data="menu_big")
    builder.button(text="🟡 Середній розмір", callback_data="menu_mid")
    builder.button(text="🎯 Допоможи вибрати", callback_data="recommend")
    builder.adjust(1)
    return builder.as_markup()

def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔴 БІГ МЕНЮ (великий розмір)",    callback_data="menu_big")
    builder.button(text="🟡 СЕРЕДНЄ МЕНЮ (середній розмір)", callback_data="menu_mid")
    builder.button(text="🎯 Допоможи вибрати",              callback_data="recommend")
    builder.adjust(1)
    return builder.as_markup()


# --- СТАРТ ---
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "👋 Привіт! Ласкаво просимо до *KOYOT* 🐺\n\n"
        "Я допоможу тобі вибрати смачне замовлення!\n\n"
        "🕐 *Години роботи:*\n"
        "Пн–Пт: 10:00 – 21:00\n\n"
        "📞 *Телефон:* 099 054 45 35\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "🤔 Яку порцію бажаєш обрати —\n*великий* чи *середній* розмір?",
        reply_markup=size_question_keyboard(),
        parse_mode="Markdown"
    )


# --- НАЗАД В ГОЛОВНЕ МЕНЮ ---
@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="🤔 Яку порцію бажаєш обрати —\n*великий* чи *середній* розмір?",
        reply_markup=size_question_keyboard(),
        parse_mode="Markdown"
    )


# ============================================
#  БІГ МЕНЮ
# ============================================

@dp.callback_query(F.data == "menu_big")
async def menu_big(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌯 В лаваші",     callback_data="big_lavash")
    builder.button(text="🍞 В булці",      callback_data="big_bulka")
    builder.button(text="🔙 Назад",        callback_data="back_main")
    builder.adjust(2, 1)
    await callback.message.edit_text(
        "🔴 *БІГ МЕНЮ* — великий розмір\n\nОбери тип:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "big_lavash")
async def big_lavash(callback: types.CallbackQuery):
    items = MENU["big_lavash"]
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=f"{item['name']} — {item['price']} ₴", callback_data=f"dish|{item['id']}|big_lavash")
    builder.button(text="🔙 Назад", callback_data="menu_big")
    builder.adjust(1)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="🔴 БІГ МЕНЮ · 🌯 *В лаваші*\n\nОбери страву:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "big_bulka")
async def big_bulka(callback: types.CallbackQuery):
    items = MENU["big_bulka"]
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=f"{item['name']} — {item['price']} ₴", callback_data=f"dish|{item['id']}|big_bulka")
    builder.button(text="🔙 Назад", callback_data="menu_big")
    builder.adjust(1)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="🔴 БІГ МЕНЮ · 🍞 *В булці*\n\nОбери страву:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


# ============================================
#  СЕРЕДНЄ МЕНЮ
# ============================================

@dp.callback_query(F.data == "menu_mid")
async def menu_mid(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌯 В лаваші",   callback_data="mid_lavash")
    builder.button(text="🍞 В булці",    callback_data="mid_bulka")
    builder.button(text="🔙 Назад",      callback_data="back_main")
    builder.adjust(2, 1)
    await callback.message.edit_text(
        "🟡 *СЕРЕДНЄ МЕНЮ* — середній розмір\n\nОбери тип:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "mid_lavash")
async def mid_lavash(callback: types.CallbackQuery):
    items = MENU["mid_lavash"]
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=f"{item['name']} — {item['price']} ₴", callback_data=f"dish|{item['id']}|mid_lavash")
    builder.button(text="🔙 Назад", callback_data="menu_mid")
    builder.adjust(1)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="🟡 СЕРЕДНЄ МЕНЮ · 🌯 *В лаваші*\n\nОбери страву:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "mid_bulka")
async def mid_bulka(callback: types.CallbackQuery):
    items = MENU["mid_bulka"]
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=f"{item['name']} — {item['price']} ₴", callback_data=f"dish|{item['id']}|mid_bulka")
    builder.button(text="🔙 Назад", callback_data="menu_mid")
    builder.adjust(1)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="🟡 СЕРЕДНЄ МЕНЮ · 🍞 *В булці*\n\nОбери страву:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


# ============================================
#  ПОКАЗ СТРАВИ З ФОТО
# ============================================

@dp.callback_query(F.data.startswith("dish|"))
async def show_dish(callback: types.CallbackQuery):
    parts = callback.data.split("|")
    # dish|id|back_category
    item_id = parts[1]
    back_cat = parts[2]
    item = ALL_ITEMS.get(item_id)

    if not item:
        await callback.answer("Страву не знайдено")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Хочу замовити!", callback_data=f"order|{item_id}")
    builder.button(text="🔙 Назад",          callback_data=back_cat)
    builder.adjust(1)

    caption = (
        f"🍽 *{item['name']}*\n\n"
        f"📝 {item['desc']}\n\n"
        f"💰 Ціна: *{item['price']} ₴*"
    )

    try:
        await callback.message.delete()
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=item["photo"],
            caption=caption,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    except Exception:
        # Якщо фото не завантажено — показуємо без фото
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=caption,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )


# ============================================
#  ЗАМОВЛЕННЯ
# ============================================

@dp.callback_query(F.data.startswith("order|"))
async def order_item(callback: types.CallbackQuery):
    item_id = callback.data.split("|")[1]
    item = ALL_ITEMS.get(item_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="📲 Написати замовлення в чат", url="https://t.me/Dato5021990")
    builder.button(text="🔙 Повернутись в меню", callback_data="back_main")
    builder.adjust(1)

    await callback.message.answer(
        f"✅ Чудовий вибір!\n\n"
        f"🍽 *{item['name']}* — {item['price']} ₴\n\n"
        f"Натисни кнопку нижче щоб написати нам замовлення в чат 👇\n\n"
        f"Смачного! 😋🐺",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


# ============================================
#  СИСТЕМА РЕКОМЕНДАЦІЙ
# ============================================

@dp.callback_query(F.data == "recommend")
async def recommend(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Дуже голодний",       callback_data="r_hungry")
    builder.button(text="😊 Середній апетит",     callback_data="r_medium")
    builder.button(text="🥗 Хочу щось легке",     callback_data="r_light")
    builder.button(text="🔙 Назад",               callback_data="back_main")
    builder.adjust(1)
    await callback.message.edit_text(
        "🎯 Допоможу вибрати!\n\nЯк ти зараз себе почуваєш?",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "r_hungry")
async def r_hungry(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌯 Люблю лаваш",   callback_data="dish|coyote|big_lavash")
    builder.button(text="🍞 Хочу в булці",  callback_data="dish|bigjo|big_bulka")
    builder.button(text="🔙 Назад",          callback_data="recommend")
    builder.adjust(1)
    await callback.message.edit_text(
        "Ти дуже голодний — беремо БІГ МЕНЮ! 💪\n\nЩо більше подобається?",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "r_medium")
async def r_medium(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌯 Сендвіч-Cheese-рол", callback_data="dish|cheeseroll|mid_lavash")
    builder.button(text="🍞 Тост з куркою",       callback_data="dish|toastchick|mid_bulka")
    builder.button(text="🌯 Загнаний Койот",      callback_data="dish|coyote|big_lavash")
    builder.button(text="🔙 Назад",               callback_data="recommend")
    builder.adjust(1)
    await callback.message.edit_text(
        "Середній апетит — є відмінні варіанти! 😋\n\nОбери що цікавить:",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "r_light")
async def r_light(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌯 Сендвіч-рол з шинкою", callback_data="dish|hamroll|mid_lavash")
    builder.button(text="🌯 Сендвіч-Cheese-рол",   callback_data="dish|cheeseroll|mid_lavash")
    builder.button(text="🍞 Тост з шинкою",         callback_data="dish|toastham|mid_bulka")
    builder.button(text="🔙 Назад",                 callback_data="recommend")
    builder.adjust(1)
    await callback.message.edit_text(
        "Хочеш щось легке — середнє меню ідеально! 🥗\n\nОбери варіант:",
        reply_markup=builder.as_markup()
    )


# ============================================
#  ЗАПУСК
# ============================================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
