import asyncio
import logging
import random
import json
import os
from datetime import datetime, timezone, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ============================================
#  ШАГ 1: ВСТАВЬ СВОЙ ТОКЕН СЮДА
# ============================================
TOKEN = "8605749499:AAGBfqpuaLuX-EtfXf_HQMsd2ZIQp-n8Ar4"
ADMIN_ID = 5320781358  # Сюди приходять відгуки

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


def get_status():
    # Часовий пояс Київ (UTC+2 / UTC+3 влітку)
    tz = timezone(timedelta(hours=3))
    now = datetime.now(tz)
    weekday = now.weekday()  # 0=Пн, 6=Нд
    hour = now.hour
    minute = now.minute
    time_now = hour * 60 + minute

    # Пн-Пт 10:00-21:00
    is_workday = weekday <= 4  # Пн-Пт
    is_open_time = 10 * 60 <= time_now < 21 * 60

    if is_workday and is_open_time:
        return "🟢 *ВІДКРИТО* · Працюємо до 21:00"
    elif weekday >= 5:
        return "🔴 *ЗАЧИНЕНО* · Вихідний день"
    elif time_now < 10 * 60:
        return "🔴 *ЗАЧИНЕНО* · Відкриємось о 10:00"
    else:
        return "🔴 *ЗАЧИНЕНО* · Відкриємось завтра о 10:00"


def size_question_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔴 Великий розмір — БІГ МЕНЮ", callback_data="menu_big")
    builder.button(text="🟡 Середній розмір", callback_data="menu_mid")
    builder.button(text="🎯 Допоможи вибрати", callback_data="recommend")
    builder.button(text="🎰 Крутилка удачі", callback_data="spin")
    builder.button(text="📍 Ми на карті", url="http://bit.ly/4lB6sM9")
    builder.button(text="💬 Підтримка / Питання", url="https://t.me/koyot_cv")
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
        f"👋 Привіт! Ласкаво просимо до *KOYOT* 🐺\n\n"
        f"{get_status()}\n\n"
        f"🕐 *Години роботи:*\n"
        f"Пн–Пт: 10:00 – 21:00\n\n"
        f"📞 *Телефон:* 099 054 45 35\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🤔 Яку порцію бажаєш обрати —\n*великий* чи *середній* розмір?",
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
    builder.button(text="🏠 Головне меню",        callback_data="back_main")
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
    builder.button(text="🏠 Головне меню", callback_data="back_main")
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
    builder.button(text="🏠 Головне меню", callback_data="back_main")
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
    builder.button(text="🏠 Головне меню",      callback_data="back_main")
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
    builder.button(text="🏠 Головне меню", callback_data="back_main")
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
    builder.button(text="🏠 Головне меню", callback_data="back_main")
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
    builder.button(text="🏠 Головне меню", callback_data="back_main")
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

    # Записуємо клієнта
    uid = callback.from_user.id
    name = callback.from_user.first_name or "—"
    username = f"@{callback.from_user.username}" if callback.from_user.username else "немає"
    tz = timezone(timedelta(hours=3))
    order_time = datetime.now(tz).strftime("%d.%m.%Y %H:%M")
    if uid not in customers:
        customers[uid] = {"name": name, "username": username, "orders": [], "count": 0}
    customers[uid]["orders"].append(f"{item['name']} — {order_time}")
    customers[uid]["count"] += 1

    builder = InlineKeyboardBuilder()
    builder.button(text="📲 Написати замовлення в чат", url="https://t.me/koyot_cv")
    builder.button(text="🏠 Головне меню", callback_data="back_main")
    builder.adjust(1)

    await callback.message.answer(
        f"✅ Чудовий вибір!\n\n"
        f"🍽 *{item['name']}* — {item['price']} ₴\n\n"
        f"Натисни кнопку нижче щоб написати нам замовлення в чат 👇\n\n"
        f"Смачного! 😋🐺",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

    # Через 2 секунди просимо залишити відгук
    await asyncio.sleep(2)
    review_builder = InlineKeyboardBuilder()
    review_builder.button(text="⭐️ 1", callback_data="review_1")
    review_builder.button(text="⭐️ 2", callback_data="review_2")
    review_builder.button(text="⭐️ 3", callback_data="review_3")
    review_builder.button(text="⭐️ 4", callback_data="review_4")
    review_builder.button(text="⭐️ 5", callback_data="review_5")
    review_builder.adjust(5)
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="💬 Як тобі наш сервіс?\nПостав оцінку від 1 до 5 ⭐️",
        reply_markup=review_builder.as_markup()
    )


# ============================================
#  СИСТЕМА РЕКОМЕНДАЦІЙ
# ============================================

@dp.callback_query(F.data == "recommend")
async def recommend(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="👉 🔥 Дуже голодний ← популярний вибір", callback_data="r_hungry")
    builder.button(text="😊 Середній апетит",     callback_data="r_medium")
    builder.button(text="🥗 Хочу щось легке",     callback_data="r_light")
    builder.button(text="🏠 Головне меню",               callback_data="back_main")
    builder.adjust(1)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="🎯 Допоможу вибрати!\n\nЯк ти зараз себе почуваєш?",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "r_hungry")
async def r_hungry(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌯 Люблю лаваш",   callback_data="dish|coyote|big_lavash")
    builder.button(text="🍞 Хочу в булці",  callback_data="dish|bigjo|big_bulka")
    builder.button(text="🔙 Назад",          callback_data="recommend")
    builder.button(text="🏠 Головне меню", callback_data="back_main")
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
    builder.button(text="🏠 Головне меню", callback_data="back_main")
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
    builder.button(text="🏠 Головне меню", callback_data="back_main")
    builder.adjust(1)
    await callback.message.edit_text(
        "Хочеш щось легке — середнє меню ідеально! 🥗\n\nОбери варіант:",
        reply_markup=builder.as_markup()
    )


# ============================================
#  ЗАПУСК
# ============================================

# ============================================
#  КРУТИЛКА УДАЧІ
# ============================================

SPIN_PRIZES = [
    {"text": "-7% на всі страви з БІГ МЕНЮ 🔥",                          "emoji": "🔥", "chance": 25},
    {"text": "-5% на всі позиції з СЕРЕДНЬОГО МЕНЮ 🎉",                   "emoji": "🎉", "chance": 25},
    {"text": "🥤 Напій у подарунок при замовленні на суму понад 1000 грн", "emoji": "🥤", "chance": 25},
    {"text": "🍖 Подвійна порція м'яса в одне блюдо із середнього меню",  "emoji": "🍖", "chance": 25},
]

# Хто вже крутив сьогодні — зберігається у файл
SPUN_FILE = "spun_today.json"

def load_spun():
    if os.path.exists(SPUN_FILE):
        with open(SPUN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_spun(data):
    with open(SPUN_FILE, "w") as f:
        json.dump(data, f)

def has_spun_today(user_id):
    data = load_spun()
    today = str(datetime.now(timezone(timedelta(hours=3))).date())
    return data.get(str(user_id)) == today

def mark_spun_today(user_id):
    data = load_spun()
    today = str(datetime.now(timezone(timedelta(hours=3))).date())
    data[str(user_id)] = today
    save_spun(data)

# Лічильник клієнтів {user_id: {"name": ..., "username": ..., "orders": [...], "count": N}}
customers = {}

# Очікуючі замовлення {username: {"user_id": ..., "name": ..., "text": ..., "item": ...}}
pending_orders = {}

# Хто зараз вводить замовлення
waiting_order = {}

@dp.callback_query(F.data == "spin")
async def spin_wheel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    # Перевіряємо чи вже крутив сьогодні
    if has_spun_today(user_id):
        await callback.answer(
            "😅 Ти вже крутив колесо сьогодні! Повертайся завтра 🌙",
            show_alert=True
        )
        return

    # Анімація рулетки
    await callback.message.delete()
    msg = await bot.send_message(
        chat_id=callback.message.chat.id,
        text="🎰 Запускаємо рулетку..."
    )

    # Всі символи рулетки
    symbols = ["🔥", "🎉", "🥤", "🍖", "⭐️", "💥", "🌀", "🎯"]

    # Швидке прокручування
    for i in range(12):
        s1 = symbols[i % len(symbols)]
        s2 = symbols[(i + 2) % len(symbols)]
        s3 = symbols[(i + 4) % len(symbols)]
        frame = "🎰 *Рулетка крутиться...*\n\n┌───────────┐\n│ " + s1 + " │ " + s2 + " │ " + s3 + " │\n└───────────┘\n\n⏳ Зачекай..."
        await msg.edit_text(frame, parse_mode="Markdown")
        await asyncio.sleep(0.15 + i * 0.04)

    # Уповільнення перед результатом
    for i in range(4):
        s1 = symbols[(i * 3) % len(symbols)]
        s2 = symbols[(i * 3 + 1) % len(symbols)]
        s3 = symbols[(i * 3 + 2) % len(symbols)]
        frame2 = "🎰 *Майже...*\n\n┌───────────┐\n│ " + s1 + " │ " + s2 + " │ " + s3 + " │\n└───────────┘\n\n🎯 Зупиняємось..."
        await msg.edit_text(frame2, parse_mode="Markdown")
        await asyncio.sleep(0.4 + i * 0.2)

    # Визначаємо приз
    weights = [p["chance"] for p in SPIN_PRIZES]
    prize = random.choices(SPIN_PRIZES, weights=weights, k=1)[0]

    # Зберігаємо що вже крутив
    mark_spun_today(user_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Головне меню", callback_data="back_main")
    builder.adjust(1)

    e = prize['emoji']
    result_text = (
        "🎰 *РЕЗУЛЬТАТ!*\n\n"
        "┌─────────────┐\n"
        f"│  {e}  │  {e}  │  {e}  │\n"
        "└─────────────┘\n\n"
        "🏆 *Ти виграв:*\n"
        f"{prize['text']}\n\n"
        "📍 _Покажи цей екран на касі!_"
    )
    await msg.edit_text(
        result_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

    # Повідомляємо адміна
    username = f"@{callback.from_user.username}" if callback.from_user.username else f"ID: {user_id}"
    first_name = callback.from_user.first_name or ""
    admin_text = "🎰 *Крутилка!*\n\nВід: " + first_name + " " + username + "\nВиграш: " + prize['text']
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        parse_mode="Markdown"
    )


# ============================================
#  ВІДГУКИ
# ============================================

REVIEW_TEXTS = {
    "review_1": "😞 Дякуємо за відгук. Нам шкода що не виправдали очікувань — передамо команді!",
    "review_2": "😕 Дякуємо! Будемо працювати краще 💪",
    "review_3": "😊 Дякуємо за оцінку! Прагнемо до 5 зірок 🌟",
    "review_4": "😃 Дякуємо! Раді що сподобалось 🐺",
    "review_5": "🤩 Дякуємо! Ти найкращий клієнт! Чекаємо знову 🐺❤️",
}

# Зберігаємо оцінки користувачів поки вони пишуть текст
user_stars = {}

@dp.callback_query(F.data.startswith("review_"))
async def handle_review(callback: types.CallbackQuery):
    stars = int(callback.data.split("_")[1])
    star_display = "⭐️" * stars + "☆" * (5 - stars)

    # Зберігаємо оцінку
    user_stars[callback.from_user.id] = stars

    # Просимо написати коментар
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Пропустити", callback_data="review_skip")
    builder.adjust(1)

    await callback.message.edit_text(
        f"{star_display}\n\n"
        f"Дякуємо за оцінку! 🙏\n\n"
        f"✍️ Хочеш залишити коментар? Напиши що думаєш про нас!\n"
        f"(або натисни Пропустити)",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "review_skip")
async def review_skip(callback: types.CallbackQuery):
    stars = user_stars.get(callback.from_user.id, 5)
    star_display = "⭐️" * stars + "☆" * (5 - stars)
    text = REVIEW_TEXTS.get(f"review_{stars}", "Дякуємо!")

    await callback.message.edit_text(f"{star_display}\n\n{text}")

    # Надсилаємо адміну без коментаря
    username = f"@{callback.from_user.username}" if callback.from_user.username else f"ID: {callback.from_user.id}"
    first_name = callback.from_user.first_name or ""
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"⭐️ *Новий відгук!*\n\n"
             f"Від: {first_name} {username}\n"
             f"Оцінка: {star_display} {stars}/5\n"
             f"Коментар: —",
        parse_mode="Markdown"
    )
    user_stars.pop(callback.from_user.id, None)


@dp.message(lambda message: message.from_user.id in user_stars)
async def handle_review_text(message: types.Message):
    stars = user_stars.get(message.from_user.id, 5)
    star_display = "⭐️" * stars + "☆" * (5 - stars)
    text = REVIEW_TEXTS.get(f"review_{stars}", "Дякуємо!")
    comment = message.text

    # Відповідь клієнту
    await message.answer(f"{star_display}\n\n{text}\n\nТвій відгук записано! 📝")

    # Надсилаємо адміну з коментарем
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    first_name = message.from_user.first_name or ""
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"⭐️ *Новий відгук!*\n\n"
             f"Від: {first_name} {username}\n"
             f"Оцінка: {star_display} {stars}/5\n"
             f"💬 Коментар: _{comment}_",
        parse_mode="Markdown"
    )
    user_stars.pop(message.from_user.id, None)


# ============================================
#  СИСТЕМА ЗАМОВЛЕНЬ
# ============================================

@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery):
    uid = callback.from_user.id
    waiting_order.pop(uid, None)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await bot.send_message(
        chat_id=uid,
        text="❌ Замовлення скасовано.",
        reply_markup=size_question_keyboard()
    )


@dp.message(lambda m: m.from_user.id in waiting_order and m.from_user.id not in user_stars)
async def receive_order_text(message: types.Message):
    uid = message.from_user.id
    order_data = waiting_order.pop(uid, {})
    item_name = order_data.get("item", "—")
    item_price = order_data.get("price", "—")
    details = message.text
    name = message.from_user.first_name or "—"
    username = message.from_user.username or ""
    username_str = f"@{username}" if username else f"ID:{uid}"

    # Зберігаємо замовлення
    pending_orders[username_str] = {
        "user_id": uid,
        "name": name,
        "item": item_name,
        "price": item_price,
        "details": details,
        "username_str": username_str
    }

    # Повідомляємо клієнта
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Головне меню", callback_data="back_main")
    builder.adjust(1)
    await message.answer(
        f"📨 *Замовлення відправлено!*\n\n"
        f"🍽 {item_name} — {item_price} ₴\n"
        f"📝 {details}\n\n"
        f"⏳ Очікуй підтвердження від закладу...",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

    # Повідомляємо адміна
    admin_text = (
        "🔔 *Нове замовлення!*\n\n"
        "👤 Клієнт: " + name + " " + username_str + "\n"
        "🍽 Страва: " + item_name + " — " + str(item_price) + " ₴\n"
        "📝 Деталі: " + details + "\n\n"
        "✅ Для підтвердження напиши:\n"
        "/order " + username_str
    )
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        parse_mode="Markdown"
    )


@dp.message(lambda m: m.text and m.text.startswith("/order") and m.from_user.id == ADMIN_ID)
async def confirm_order(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❗️ Використання: /order @username або /order ID:12345")
        return

    username_str = parts[1]
    order = pending_orders.pop(username_str, None)

    if not order:
        await message.answer(f"❗️ Замовлення від {username_str} не знайдено.")
        return

    # Повідомляємо клієнта
    await bot.send_message(
        chat_id=order["user_id"],
        text=f"🎉 *Твоє замовлення прийнято!*\n\n"
             f"🍽 *{order['item']}* — {order['price']} ₴\n"
             f"📝 {order['details']}\n\n"
             f"⏰ Очікуй — ми вже готуємо!\n"
             f"Смачного! 😋🐺",
        parse_mode="Markdown"
    )

    # Записуємо в лічильник
    uid = order["user_id"]
    tz = timezone(timedelta(hours=3))
    order_time = datetime.now(tz).strftime("%d.%m.%Y %H:%M")
    if uid not in customers:
        customers[uid] = {"name": order["name"], "username": username_str, "orders": [], "count": 0}
    customers[uid]["orders"].append(f"{order['item']} — {order_time}")
    customers[uid]["count"] += 1

    await message.answer(f"✅ Замовлення {username_str} підтверджено!")


# ============================================
#  СТАТИСТИКА ДЛЯ АДМІНА
# ============================================

@dp.message(lambda m: m.text == "/stats" and m.from_user.id == ADMIN_ID)
async def show_stats(message: types.Message):
    if not customers:
        await message.answer("📊 Поки що замовлень немає.")
        return

    total_orders = sum(c["count"] for c in customers.values())
    total_clients = len(customers)

    text = f"📊 *Статистика KOYOT*\n\n"
    text += f"👥 Всього клієнтів: *{total_clients}*\n"
    text += f"🛒 Всього замовлень: *{total_orders}*\n\n"
    text += "─────────────────\n"

    # Топ 10 клієнтів
    sorted_customers = sorted(customers.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
    for i, (uid, data) in enumerate(sorted_customers, 1):
        last_order = data["orders"][-1].split(" — ")[-1] if data["orders"] else "—"
        text += f"{i}. *{data['name']}* {data['username']}\n"
        text += f"   🛒 Замовлень: {data['count']} · Останнє: {last_order}\n"

    await message.answer(text, parse_mode="Markdown")


@dp.message(lambda m: m.text == "/clients" and m.from_user.id == ADMIN_ID)
async def show_clients(message: types.Message):
    if not customers:
        await message.answer("👥 Поки що клієнтів немає.")
        return

    text = "👥 *Всі клієнти:*\n\n"
    for uid, data in customers.items():
        text += f"• *{data['name']}* {data['username']}\n"
        for order in data["orders"][-3:]:  # Останні 3 замовлення
            text += f"  └ {order}\n"
        text += "\n"

    await message.answer(text, parse_mode="Markdown")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
