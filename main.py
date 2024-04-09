import math
import signal
import sqlite3
import sys

import requests
import telebot
from bs4 import BeautifulSoup
from telebot import types

TOKEN = '7055838467:AAGI_5JLUNkVwt4ljGpUI2pv43841mTEgxs'
# TOKEN = '6513736156:AAEP4uwZQLDcQxk6C8KV8YDMWlvb_dri-0s'

bot = telebot.TeleBot(TOKEN)
db_filename = 'ttbot.db'
conn = sqlite3.connect(db_filename, check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT
    )
''')
conn.commit()

# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id

    # Проверка наличия пользователя в базе данных
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user is None:
        # Если пользователь новый, добавляем его в базу данных с значениями по умолчанию
        cursor.execute('''
            INSERT INTO users (user_id, name, username)
            VALUES (?, ?, ?)
        ''', (user_id, message.from_user.first_name, message.from_user.username))
        conn.commit()

    # Send welcome message
    if message.chat.type == 'private':
        # Send welcome message only if it's a private chat
        with open('welcome.jpg', 'rb') as photo:
            bot.send_photo(message.chat.id, photo,
                           caption="Привет! Этот бот отслеживает данные токенов на TON. Продукт был разработан @TokenInfinity. Бота необязательно добавлять в чат.\nНажмите ниже:",
                           reply_markup=create_inline_keyboard(), parse_mode="Markdown")

def create_inline_keyboard():
    # This function creates an inline keyboard with buttons for Help and Listing
    keyboard = types.InlineKeyboardMarkup()
    help_button = types.InlineKeyboardButton("📖 Помощь", callback_data="help")
    listing_button = types.InlineKeyboardButton("🪙 Листинг", callback_data="listing")
    keyboard.add(help_button)
    keyboard.add(listing_button)
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data == 'help')
def help_callback(call):
    try:
        with open('helptt.jpg', 'rb') as photo:
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("« Назад", callback_data="back")
            keyboard.add(back_button) # Use the create_back_button function

            # If the original message contains media, edit it
            if call.message.photo:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=types.InputMediaPhoto(media=photo),
                    reply_markup=keyboard
                )
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=generate_help_message(),  # Include the message as the caption
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            else:
                # If the original message doesn't contain media, send the photo along with the caption
                bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=photo,
                    caption=generate_help_message(),
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"An error occurred: {e}")


def generate_help_message():
    return (
        "Чтобы начать пользоваться ботом, введите на клавиатуре: \n\n"
        "— `@TrackerTonBot ton`\n\n"
        "Появится инлайн-режим, где вы можете нажать на токен и получить данные по нему. Используйте любой тикер, чтобы получить данные о токене.\n\n"
        "На данный момент доступны следующие токены:\n"
        "[INFT](https://t.me/TokenInfinity), [LKY](https://t.me/lkyton), [UNIC](https://t.me/unicorncoinmain), [TRIBE](https://t.me/tribes_ton), "
        "[STBL](https://t.me/stablemetal), [IVS](https://t.me/StalinFoundation), [BOLT](https://t.me/boltfoundation), [DFC](https://t.me/de_findercapital), "
        "[GRAM](https://t.me/gramcoinorg), [DINJA](https://t.me/tonmelonfest), [ALL](https://t.me/allweton), [HYDRA](https://t.me/Ton_HYDRAcoin), "
        "[RCAT](https://t.me/RocketCatsTon), [EXC](https://t.me/exc_coin), [SCALE](https://t.me/Scaleton_University_RU), [STON](https://t.me/stonfidex), "
        "[ARBUZ](https://t.me/tonarbuz), [HMSTR](https://t.me/LoLZ_HAMSTERS_GODS), [SCAM](https://t.me/scamjettonton), [KINGY](https://t.me/investkingyru), "
        "[UP](https://t.me/TonUP_io), [FISH](https://t.me/tonfish_tg), [TPET](https://t.me/tonfish_tg), [FNZ](https://t.me/fanzeelabs), "
        "[PUNK](https://t.me/tonpunks), [JETTON](https://t.me/JetTon_Official), [ULT](https://t.me/ultronlive), [SOCK](https://t.me/boltwifsock), "
        "[STATHAM](https://t.me/Statham_TON), [SLOW](https://t.me/slowpoke_investments), [ANON](https://t.me/anon_club), [REDO](https://t.me/redoton), "
        "[DUCK](https://t.me/duckcoin), [WNOT](https://t.me/shardify), [MRDN](https://t.me/meridian_wtf), [POT](https://t.me/jackpot_ton), "
        "[BLKC](https://t.me/blackhatcoin), [DRA](https://t.me/dragons_ton), [BLACK](https://t.me/Black_Casino_Token), [LIFEYT](https://t.me/lifeyt) "

    )

@bot.callback_query_handler(func=lambda call: call.data == 'listing')
def listing_callback(call):
    try:
        with open('listingtt.jpg', 'rb') as photo:
            keyboard = types.InlineKeyboardMarkup()
            dedust_button = types.InlineKeyboardButton("DeDust", url="https://dedust.io/swap/TON/EQAEfUNvB01k3khyyMJeQu6Y609TOPtm_-Mn0-12NJb4SXwR")
            back_button = types.InlineKeyboardButton("« Назад", callback_data="back")
            keyboard.add(dedust_button)
            keyboard.add(back_button)

            bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=types.InputMediaPhoto(media=photo),
                reply_markup=keyboard
            )
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="Для размещения вашего токена в боте необходимо оплатить:`4 TON в токенах $INFT`. "
                        "Для любых вопросов обращайтесь к администратору @SoftwareMaestro.",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"An error occurred: {e}")


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back_callback(call):
    try:
        with open('welcome.jpg', 'rb') as photo:
            keyboard = create_inline_keyboard()
            bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=types.InputMediaPhoto(media=photo),
                reply_markup=keyboard
            )
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="Привет! Этот бот отслеживает данные токенов на TON. Продукт был разработан @TokenInfinity. Бота необязательно добавлять в чат.\nНажмите ниже:",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"An error occurred: {e}")


# Обработка команды /stats
@bot.message_handler(commands=['stats'])
def handle_stats(message):
    # Проверяем, является ли отправитель администратором
    if message.from_user.id == 1196918969:
        # Запрос для подсчета количества пользователей в базе данных
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]

        # Отправляем сообщение с количеством пользователей
        bot.reply_to(message, f"Количество пользователей в боте: {count}")
    else:
        # Если отправитель не является администратором, отправляем сообщение об ошибке доступа
        bot.reply_to(message, "Извините, у вас нет доступа к этой команде.")


# Обработка команды /post
@bot.message_handler(commands=['post'])
def handle_post(message):
    # Проверяем, является ли отправитель администратором
    if message.from_user.id == 1196918969:
        # Получаем текст сообщения из параметров команды
        text = message.text.replace("/post ", "")

        # Запрос для получения всех пользователей из базы данных
        cursor.execute('SELECT user_id FROM users')
        users = cursor.fetchall()

        # Отправляем сообщение каждому пользователю
        for user_id in users:
            try:
                # Отправляем сообщение пользователю
                bot.send_message(user_id[0], text)
            except telebot.apihelper.ApiException as e:
                # Если пользователь заблокировал бота, продолжаем отправку сообщений
                continue
        # Отправляем подтверждение об успешной отправке сообщений
        bot.reply_to(message, f"Сообщение успешно отправлено всем пользователям.")
    else:
        # Если отправитель не является администратором, отправляем сообщение об ошибке доступа
        bot.reply_to(message, "Извините, у вас нет доступа к этой команде.")


# Функция для сокращения чисел
def shorten_number(number):
    suffixes = ['', 'K', 'M', 'B', 'T']
    if number < 1000:
        return str(number)
    else:
        exp = int(math.log(number, 1000))
        short_number = round(number / (1000 ** exp), 2)
        return f"{short_number}{suffixes[exp]}"


# @bot.inline_handler(func=lambda query: query.query.lower() == 'top')
# def query_tokens(inline_query):
#     try:
#         # Данные для токена TON
#         url1 = 'https://coinmarketcap.com/currencies/toncoin/'
#         class_name = 'sc-f70bb44c-0 jxpCgO base-text'  # Это имя класса может потребоваться обновить
#         api_url1 = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c/pools?page=1'
#         price1, error1 = fetch_crypto_price(url1, class_name)
#         fdv_usd1, price_change1, api_error1 = fetch_token_data(api_url1)
#
#         # Данные для токена LKY
#         price2, error2 = fetch_crypto_price_lky()
#         fdv_usd2, volume_24h2, liquidity2, price_change2, api_error2 = fetch_lky_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCyDhcASwIm8-eVVTzMEESYAeQ7ettasfuGXUG1tkDwVJbc/pools?page=1')
#
#         # Данные для токена INFT
#         price3, error3 = fetch_inft_price_from_api()
#         fdv_usd3, volume_24h3, liquidity3, price_change3, api_error3 = fetch_inft_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAEfUNvB01k3khyyMJeQu6Y609TOPtm_-Mn0-12NJb4SXwR/pools?page=1')
#
#         # Данные для токена TRIBE
#         price4, error4 = fetch_tribe_price_from_api()
#         fdv_usd4, volume_24h4, liquidity4, price_change4, api_error4 = fetch_tribe_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCcXKwYGCCZnzQj9vwwg8Y-F3d8H7cow-Mwgj8pTFruBfP8/pools?page=1')
#
#         # Данные для токена STBL
#         price5, error5 = fetch_stbl_price_from_api()
#         fdv_usd5, volume_24h5, liquidity5, price_change5, api_error5 = fetch_stbl_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD5ty5IxV3HECEY1bbbdd7rNNY-ZcA-pAIGQXyyRZRED9v3/pools?page=1')
#
#         price6, error6 = fetch_unic_price_from_api()
#         fdv_usd6, volume_24h6, liquidity6, price_change6, api_error6 = fetch_unic_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQB2lbt2s_jdUW3OoUIb7-9RoK2UeGXmgC7BnOwgK6P_JTrm/pools?page=1')
#
#         # Данные для токена IVS
#         price7, error7 = fetch_ivs_price_from_api()
#         fdv_usd7, volume_24h7, liquidity7, price_change7, api_error7 = fetch_ivs_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQACGPrFHWCy9QmeFXPqvZflyoeBb5grVQxAaucF0hNd1sEs/pools?page=1')
#
#         results = []
#
#         # Создаем объекты InlineQueryResultArticle для токена TON
#         if price1 and fdv_usd1:
#             if not error1 and not api_error1:
#                 fdv_usd_formatted1 = '{:,.0f}'.format(float(fdv_usd1))
#                 emoji1 = '🔴' if float(price_change1) < 0 else '🟢'
#                 updated_text1 = f'💎 1 TON = {price1}  •  {emoji1}{price_change1}%\n\nMarket Cap: ${fdv_usd_formatted1}'
#                 thumb_url1 = 'https://danil1110.github.io/NFTcollcetion/TonImg.png'
#                 article_content1 = types.InputTextMessageContent(message_text=updated_text1)
#                 refresh_button1 = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price")
#                 keyboard1 = types.InlineKeyboardMarkup().add(refresh_button1)
#                 r1 = types.InlineQueryResultArticle(
#                     id='1',
#                     title='Курс 💎 TON в 💲USD',
#                     description=f'💎 1 TON = {price1}\nMarket Cap: ${fdv_usd_formatted1}',
#                     input_message_content=article_content1,
#                     thumbnail_url=thumb_url1,
#                     reply_markup=keyboard1
#                 )
#                 results.append(r1)
#
#         # Создаем объекты InlineQueryResultArticle для токена LKY
#         if price2 and fdv_usd2:
#             if not error2 and not api_error2:
#                 liq_formatted2 = shorten_number(float(liquidity2))
#                 fdv_usd_formatted2 = shorten_number(float(fdv_usd2))
#                 volume_24h_formatted2 = ""
#                 if float(volume_24h2) < 1000:
#                     volume_24h_formatted2 = "{:.2f}".format(float(volume_24h2))
#                 else:
#                     volume_24h_formatted2 = shorten_number(float(volume_24h2))
#                 emoji2 = '🔴' if float(price_change2) < 0 else '🟢'
#                 updated_text2 = f'🍀 1 LKY = ${price2}  •  {emoji2}{price_change2}%\n\nLiquidity: ${liq_formatted2}  •  Volume 24h: ${volume_24h_formatted2}\n\nMarket Cap: ${fdv_usd_formatted2}'
#                 thumb_url2 = 'https://cache.tonapi.io/imgproxy/4DGuXDEqF18fzPL9cNlSuT5DFwoa1PKx-SjWJGWZpj8/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLmliYi5jby9YN3d2RDFQL01lYW5pbmctb2YtYS1Gb3VyLWxlYWYtQ2xvdmVyLVNpZ2h0aW5nLTIuanBn.webp'
#                 article_content2 = types.InputTextMessageContent(message_text=updated_text2)
#                 buy1_button2 = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/LKY")
#                 buy2_button2 = types.InlineKeyboardButton(text="STON.fi", url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=LKY")
#                 refresh_button2 = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_lky")
#                 keyboard2 = types.InlineKeyboardMarkup()
#                 keyboard2.add(buy1_button2, buy2_button2)
#                 keyboard2.add(refresh_button2)
#                 r2 = types.InlineQueryResultArticle(
#                     id='2',
#                     title='Курс 🍀 LKY в 💲USD',
#                     description=f'🍀 1 LKY = ${price2}\nMarket Cap: ${fdv_usd_formatted2}',
#                     input_message_content=article_content2,
#                     thumbnail_url=thumb_url2,
#                     reply_markup=keyboard2
#                 )
#                 results.append(r2)
#
#         # Создаем объекты InlineQueryResultArticle для токена INFT
#         if price3 and fdv_usd3:
#             if not error3 and not api_error3:
#                 liq_formatted3 = shorten_number(float(liquidity3))
#                 fdv_usd_formatted3 = shorten_number(float(fdv_usd3))
#                 volume_24h_formatted3 = ""
#                 if float(volume_24h3) < 1000:
#                     volume_24h_formatted3 = "{:.2f}".format(float(volume_24h3))
#                 else:
#                     volume_24h_formatted3 = shorten_number(float(volume_24h3))
#                 emoji3 = '🔴' if float(price_change3) < 0 else '🟢'
#                 updated_text3 = f'♾️ 1 INFT = ${price3}  •  {emoji3}{price_change3}%\n\nLiquidity: ${liq_formatted3}  •  Volume 24h: ${volume_24h_formatted3}\n\nMarket Cap: ${fdv_usd_formatted3}'
#                 thumb_url3 = 'https://cache.tonapi.io/imgproxy/Pj8Zn7cD2mRcQ4_5RR3FIJN_sYn8KwYzcJIXy1PCi2A/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pbWFnZXVwLnJ1L2ltZzIyNy80NzY1NDc1L2ltZ18yMDI0MDMxNV8wNzE0MzhfODg1LmpwZw.webp'
#                 article_content3 = types.InputTextMessageContent(message_text=updated_text3)
#                 buy1_button3 = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EQAEfUNvB01k3khyyMJeQu6Y609TOPtm_-Mn0-12NJb4SXwR")
#                 refresh_button3 = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_inft")
#                 keyboard3 = types.InlineKeyboardMarkup()
#                 keyboard3.add(buy1_button3)
#                 keyboard3.add(refresh_button3)
#                 r3 = types.InlineQueryResultArticle(
#                     id='3',
#                     title='Курс ♾️ INFT в 💲USD',
#                     description=f'♾️ 1 INFT = ${price3}\nMarket Cap: ${fdv_usd_formatted3}',
#                     input_message_content=article_content3,
#                     thumbnail_url=thumb_url3,
#                     reply_markup=keyboard3
#                 )
#                 results.append(r3)
#
#         # Создаем объекты InlineQueryResultArticle для токена TRIBE
#         if price4 and fdv_usd4:
#             if not error4 and not api_error4:
#                 liq_formatted4 = shorten_number(float(liquidity4))
#                 fdv_usd_formatted4 = shorten_number(float(fdv_usd4))
#                 volume_24h_formatted4 = ""
#                 if float(volume_24h4) < 1000:
#                     volume_24h_formatted4 = "{:.2f}".format(float(volume_24h4))
#                 else:
#                     volume_24h_formatted4 = shorten_number(float(volume_24h4))
#                 emoji4 = '🔴' if float(price_change4) < 0 else '🟢'
#                 updated_text4 = f'👨‍👨‍👧‍👦 1 TRIBE = ${price4}  •  {emoji4}{price_change4}%\n\nLiquidity: ${liq_formatted4}  •  Volume 24h: ${volume_24h_formatted4}\n\nMarket Cap: ${fdv_usd_formatted4}'
#                 thumb_url4 = 'https://cache.tonapi.io/imgproxy/C1CXpOhWuoQmDIlthqD9pLvFnpGdJGWcL8MywIH02J8/rs:fill:200:200:1/g:no/aHR0cHM6Ly9iYWZ5YmVpYXpia2oyNnJrdTZyZXIzaDJybGhwcGFoc25xbmVjNXllbmJyem0yNjYydWdzdWRzZWxxYS5pcGZzLnczcy5saW5rL3RyaWJldG9uMjU2LnBuZw.webp'
#                 article_content4 = types.InputTextMessageContent(message_text=updated_text4)
#                 buy1_button4 = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/TRIBE")
#                 buy2_button4 = types.InlineKeyboardButton(text="STON.fi", url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=TRIBE")
#                 refresh_button4 = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_tribe")
#                 keyboard4 = types.InlineKeyboardMarkup()
#                 keyboard4.add(buy1_button4, buy2_button4)
#                 keyboard4.add(refresh_button4)
#                 r4 = types.InlineQueryResultArticle(
#                     id='4',
#                     title='Курс 👨‍👨‍👧‍👦 TRIBE в 💲USD',
#                     description=f'👨‍👨‍👧‍👦 1 TRIBE = ${price4}\nMarket Cap: ${fdv_usd_formatted4}',
#                     input_message_content=article_content4,
#                     thumbnail_url=thumb_url4,
#                     reply_markup=keyboard4
#                 )
#                 results.append(r4)
#
#         # Создаем объекты InlineQueryResultArticle для токена STBL
#         if price5 and fdv_usd5:
#             if not error5 and not api_error5:
#                 liq_formatted5 = shorten_number(float(liquidity5))
#                 fdv_usd_formatted5 = shorten_number(float(fdv_usd5))
#                 volume_24h_formatted5 = ""
#                 if float(volume_24h5) < 1000:
#                     volume_24h_formatted5 = "{:.2f}".format(float(volume_24h5))
#                 else:
#                     volume_24h_formatted5 = shorten_number(float(volume_24h5))
#                 emoji5 = '🔴' if float(price_change5) < 0 else '🟢'
#                 updated_text5 = f'🏅 1 STBL = ${price5}  •  {emoji5}{price_change5}%\n\nLiquidity: ${liq_formatted5}  •  Volume 24h: ${volume_24h_formatted5}\n\nMarket Cap: ${fdv_usd_formatted5}'
#                 thumb_url5 = 'https://cache.tonapi.io/imgproxy/t-4hk54FgHpwh0ErqRSIJWyJNIMeF-9v5V2t8omKAHo/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLmliYi5jby9IWWNzaHF2L3N0YmwtMjU2LnBuZw.webp'
#                 article_content5 = types.InputTextMessageContent(message_text=updated_text5)
#                 buy1_button5 = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/STBL")
#                 buy2_button5 = types.InlineKeyboardButton(text="STON.fi", url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=STBL")
#                 refresh_button5 = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_stbl")
#                 keyboard5 = types.InlineKeyboardMarkup()
#                 keyboard5.add(buy1_button5, buy2_button5)
#                 keyboard5.add(refresh_button5)
#                 r5 = types.InlineQueryResultArticle(
#                     id='5',
#                     title='Курс 🏅 STBL в 💲USD',
#                     description=f'🏅 1 STBL = ${price5}\nMarket Cap: ${fdv_usd_formatted5}',
#                     input_message_content=article_content5,
#                     thumbnail_url=thumb_url5,
#                     reply_markup=keyboard5
#                 )
#                 results.append(r5)
#
#
#         # if price6 and fdv_usd6:
#         #     if not error6 and not api_error6:
#         #         liq_formatted6 = shorten_number(float(liquidity6))
#         #         fdv_usd_formatted6 = shorten_number(float(fdv_usd6))
#         #         volume_24h_formatted6 = "{:.2f}".format(float(volume_24h6)) if float(
#         #             volume_24h6) < 1000 else shorten_number(float(volume_24h6))
#         #         emoji6 = '🔴' if float(price_change6) < 0 else '🟢'
#         #         updated_text6 = f'🦄 1 UNIC = ${price6}  •  {emoji6}{price_change6}%\n\nLiquidity: ${liq_formatted6}  •  Volume 24h: ${volume_24h_formatted6}\n\nMarket Cap: ${fdv_usd_formatted6}'
#         #         thumb_url6 = 'https://cache.tonapi.io/imgproxy/UvPP-mdqRFu2diEOk2ztWog_Xz5TRm08-kxZdvHyEh0/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLmliYi5jby8wck5nQ2R0L3VuaWMyNTZ4MjU2LnBuZw.webp'
#         #         article_content6 = types.InputTextMessageContent(message_text=updated_text6)
#         #         keyboard = types.InlineKeyboardMarkup()
#         #         buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/UNIC")
#         #         refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_unic")
#         #         keyboard.add(buy_button)
#         #         keyboard.add(refresh_button)
#         #         r6 = types.InlineQueryResultArticle(
#         #             id='6',
#         #             title='Курс 🦄 UNIC в 💲USD',
#         #             description=f'🦄 1 UNIC = ${price6}\nMarket Cap: ${fdv_usd_formatted6}',
#         #             input_message_content=article_content6,
#         #             thumbnail_url=thumb_url6,
#         #             reply_markup=keyboard
#         #         )
#         #         results.append(r6)
#         #
#         # # Создаем объекты InlineQueryResultArticle для токена IVS
#         # if price7 and fdv_usd7:
#         #     if not error7 and not api_error7:
#         #         liq_formatted7 = shorten_number(float(liquidity7))
#         #         fdv_usd_formatted7 = shorten_number(float(fdv_usd7))
#         #         volume_24h_formatted7 = "{:.2f}".format(float(volume_24h7)) if float(
#         #             volume_24h7) < 1000 else shorten_number(float(volume_24h7))
#         #         emoji7 = '🔴' if float(price_change7) < 0 else '🟢'
#         #         updated_text7 = f'⭐ 1 IVS = ${price7}  •  {emoji7}{price_change7}%\n\nLiquidity: ${liq_formatted7}  •  Volume 24h: ${volume_24h_formatted7}\n\nMarket Cap: ${fdv_usd_formatted7}'
#         #         thumb_url7 = 'https://cache.tonapi.io/imgproxy/_T8MQV5nrm3xlePtrP8UiAJKJ6VGFNSVld37YqCYYQ0/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1N0YWxpbkZvdW5kYXRpb24vSW1hZ2VzL21haW4vU3RhbGluTG9nby5wbmc.webp'
#         #         article_content7 = types.InputTextMessageContent(message_text=updated_text7)
#         #         keyboard = types.InlineKeyboardMarkup()
#         #         buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/IVS")
#         #         refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_ivs")
#         #         keyboard.add(buy_button)
#         #         keyboard.add(refresh_button)
#         #         r7 = types.InlineQueryResultArticle(
#         #             id='7',
#         #             title='Курс ⭐ IVS в 💲USD',
#         #             description=f'⭐ 1 IVS = ${price7}\nMarket Cap: ${fdv_usd_formatted7}',
#         #             input_message_content=article_content7,
#         #             thumbnail_url=thumb_url7,
#         #             reply_markup=keyboard
#         #         )
#         #         results.append(r7)
#
#         # # Добавьте ссылку для токена BOLT
#         # price8, error8 = fetch_bolt_price_from_api()
#         # fdv_usd8, volume_24h8, liquidity8, price_change8, api_error8 = fetch_bolt_data(
#         #     'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD0vdSA_NedR9uvbgN9EikRX-suesDxGeFg69XQMavfLqIw/pools?page=1')
#         #
#         # # Добавьте ссылку для токена DFC
#         # price9, error9 = fetch_dfc_price_from_api()
#         # fdv_usd9, volume_24h9, liquidity9, price_change9, api_error9 = fetch_dfc_data(
#         #     'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD26zcd6Cqpz7WyLKVH8x_cD6D7tBrom6hKcycv8L8hV0GP/pools?page=1')
#         #
#         # # Создаем объекты InlineQueryResultArticle для токена BOLT
#         # if price8 and fdv_usd8:
#         #     if not error8 and not api_error8:
#         #         liq_formatted8 = shorten_number(float(liquidity8))
#         #         fdv_usd_formatted8 = shorten_number(float(fdv_usd8))
#         #         volume_24h_formatted8 = "{:.2f}".format(float(volume_24h8)) if float(
#         #             volume_24h8) < 1000 else shorten_number(float(volume_24h8))
#         #         emoji8 = '🔴' if float(price_change8) < 0 else '🟢'
#         #         updated_text8 = f'🔩 1 BOLT = ${price8}  •  {emoji8}{price_change8}%\n\nLiquidity: ${liq_formatted8}  •  Volume 24h: ${volume_24h_formatted8}\n\nMarket Cap: ${fdv_usd_formatted8}'
#         #         thumb_url8 = 'https://cache.tonapi.io/imgproxy/05DkTmM2Eu4YZX-ED0eQpRS8U1q7SbD3o1GC5r5ZTBw/rs:fill:200:200:1/g:no/aHR0cHM6Ly9jbG91ZGZsYXJlLWlwZnMuY29tL2lwZnMvUW1YNDdkb2RVZzFhY1hveFlEVUxXVE5mU2hYUlc1dUhyQ21vS1NVTlI5eEtRdw.webp'  # Замените на реальную ссылку на изображение
#         #         article_content8 = types.InputTextMessageContent(message_text=updated_text8)
#         #         keyboard = types.InlineKeyboardMarkup()
#         #         buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/BOLT")
#         #         refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_bolt")
#         #         keyboard.add(buy_button)
#         #         keyboard.add(refresh_button)
#         #         r8 = types.InlineQueryResultArticle(
#         #             id='8',
#         #             title='Курс 🔩 BOLT в 💲USD',
#         #             description=f'🔩 1 BOLT = ${price8}\nMarket Cap: ${fdv_usd_formatted8}',
#         #             input_message_content=article_content8,
#         #             thumbnail_url=thumb_url8,
#         #             reply_markup=keyboard
#         #         )
#         #         results.append(r8)
#         #
#         # # Создаем объекты InlineQueryResultArticle для токена DFC
#         # if price9 and fdv_usd9:
#         #     if not error9 and not api_error9:
#         #         liq_formatted9 = shorten_number(float(liquidity9))
#         #         fdv_usd_formatted9 = shorten_number(float(fdv_usd9))
#         #         volume_24h_formatted9 = "{:.2f}".format(float(volume_24h9)) if float(
#         #             volume_24h9) < 1000 else shorten_number(float(volume_24h9))
#         #         emoji9 = '🔴' if float(price_change9) < 0 else '🟢'
#         #         updated_text9 = f'🔎 1 DFC = ${price9}  •  {emoji9}{price_change9}%\n\nLiquidity: ${liq_formatted9}  •  Volume 24h: ${volume_24h_formatted9}\n\nMarket Cap: ${fdv_usd_formatted9}'
#         #         thumb_url9 = 'https://cache.tonapi.io/imgproxy/TENmVD1ZlCwI7F4dyM9k6PPyLzMrd7rZHIAyeom79SA/rs:fill:200:200:1/g:no/aHR0cHM6Ly90YW4tdG91Z2gtc2x1Zy0zNTEubXlwaW5hdGEuY2xvdWQvaXBmcy9RbVhRb2pKVVB2a0dDQ2VSOVF1OFd3bWNaRjFnTERZMjhlcExMaFBZdkR5OFRr.webp'  # Замените на реальную ссылку на изображение
#         #         article_content9 = types.InputTextMessageContent(message_text=updated_text9)
#         #         keyboard = types.InlineKeyboardMarkup()
#         #         buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DFC")
#         #         buy_button2 = types.InlineKeyboardButton(text="STON.fi",
#         #                                                  url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=DFC")
#         #         refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_dfc")
#         #         keyboard.add(buy_button, buy_button2)
#         #         keyboard.add(refresh_button)
#         #         r9 = types.InlineQueryResultArticle(
#         #             id='9',
#         #             title='Курс 🔎 DFC в 💲USD',
#         #             description=f'🔎 1 DFC = ${price9}\nMarket Cap: ${fdv_usd_formatted9}',
#         #             input_message_content=article_content9,
#         #             thumbnail_url=thumb_url9,
#         #             reply_markup=keyboard
#         #         )
#         #         results.append(r9)
#         #
#         # price10, error10 = fetch_gram_price_from_api()
#         # fdv_usd10, volume_24h10, liquidity10, price_change10, api_error10 = fetch_gram_data(
#         #     'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC47093oX5Xhb0xuk2lCr2RhS8rj-vul61u4W2UH5ORmG_O/pools?page=1')
#         #
#         # # Data for DINJA token
#         # price11, error11 = fetch_dinja_price_from_api()
#         # fdv_usd11, volume_24h11, liquidity11, price_change11, api_error11 = fetch_dinja_data(
#         #     'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQByLZOaBbpr9EwNonXKEfkkZL1viNsYHezxw5CVK4Bh0zEb/pools?page=1')
#         #
#         # # Object creation and handling logic for GRAM token
#         # if price10 and fdv_usd10:
#         #     if not error10 and not api_error10:
#         #         liq_formatted10 = shorten_number(float(liquidity10))
#         #         fdv_usd_formatted10 = shorten_number(float(fdv_usd10))
#         #         volume_24h_formatted10 = "{:.2f}".format(float(volume_24h10)) if float(
#         #             volume_24h10) < 1000 else shorten_number(float(volume_24h10))
#         #         emoji10 = '🔴' if float(price_change10) < 0 else '🟢'
#         #         updated_text10 = f'◼️ 1 GRAM = ${price10}  •  {emoji10}{price_change10}%\n\nMarket Cap: ${fdv_usd_formatted10}'
#         #         thumb_url10 = 'https://cache.tonapi.io/imgproxy/lNoY3YdNeBug53ixjK6hxT6XIX3_xoIYNqv-ykIQ1Aw/rs:fill:200:200:1/g:no/aHR0cHM6Ly9ncmFtY29pbi5vcmcvaW1nL2ljb24ucG5n.webp'   # Replace this with the actual thumbnail URL for GRAM
#         #         article_content10 = types.InputTextMessageContent(message_text=updated_text10)
#         #         keyboard = types.InlineKeyboardMarkup()
#         #         buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/GRAM")
#         #         buy_button2 = types.InlineKeyboardButton(text="STON.fi",
#         #                                                  url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=GRAM")
#         #         refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_gram")
#         #         keyboard.add(buy_button, buy_button2)
#         #         keyboard.add(refresh_button)
#         #
#         #         r10 = types.InlineQueryResultArticle(
#         #             id='10',
#         #             title='Курс ◼️ GRAM в 💲USD',
#         #             description=f'◼️ 1 GRAM = ${price10}\nMarket Cap: ${fdv_usd_formatted10}',
#         #             input_message_content=article_content10,
#         #             thumbnail_url=thumb_url10,
#         #             reply_markup=keyboard
#         #         )
#         #         results.append(r10)
#         #
#         # # Object creation and handling logic for DINJA token
#         # if price11 and fdv_usd11:
#         #     if not error11 and not api_error11:
#         #         liq_formatted11 = shorten_number(float(liquidity11))
#         #         fdv_usd_formatted11 = shorten_number(float(fdv_usd11))
#         #         volume_24h_formatted11 = "{:.2f}".format(float(volume_24h11)) if float(
#         #             volume_24h11) < 1000 else shorten_number(float(volume_24h11))
#         #         emoji11 = '🔴' if float(price_change11) < 0 else '🟢'
#         #         updated_text11 = f'🍈 1 DINJA = ${price11}  •  {emoji11}{price_change11}%\n\nMarket Cap: ${fdv_usd_formatted11}'
#         #         thumb_url11 = 'https://cache.tonapi.io/imgproxy/efWWgdJgqeiju2tCSsIeme0Aug1mA1PtaGjfWe8Qnys/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1dhdmVzVGlwQm90L0RJTkpBL21haW4vRElOSkEucG5n.webp'  # Replace this with the actual thumbnail URL for DINJA
#         #         article_content11 = types.InputTextMessageContent(message_text=updated_text11)
#         #         keyboard11 = types.InlineKeyboardMarkup()
#         #         buy_button11 = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DINJA")
#         #         refresh_button11 = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_dinja")
#         #         keyboard11.add(buy_button11)
#         #         keyboard11.add(refresh_button11)
#         #         r11 = types.InlineQueryResultArticle(
#         #             id='11',
#         #             title='Курс 🍈 DINJA в 💲USD',
#         #             description=f'🍈 1 DINJA = ${price11}\nMarket Cap: ${fdv_usd_formatted11}',
#         #             input_message_content=article_content11,
#         #             thumbnail_url=thumb_url11,
#         #             reply_markup=keyboard11
#         #         )
#         #         results.append(r11)
#         #
#         # price12, error12 = fetch_all_price_from_api()
#         # fdv_usd12, volume_24h12, liquidity12, price_change12, api_error12 = fetch_all_data(
#         #     'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDlnVo-6abJzyHlU8uB7pRjE7OIKt4HTTDPG4hfwOf5jTPg/pools?page=1')
#         #
#         # # Setup for token HYDRA
#         # price13, error13 = fetch_hydra_price_from_api()
#         # fdv_usd13, volume_24h13, liquidity13, price_change13, api_error13 = fetch_hydra_data(
#         #     'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD4P32U10snNoIavoq6cYPTQR82ewAjO20epigrWRAup54_/pools?page=1')
#         #
#         # if price12 and fdv_usd12:
#         #     if not error12 and not api_error12:
#         #         liq_formatted12 = shorten_number(float(liquidity12))
#         #         fdv_usd_formatted12 = shorten_number(float(fdv_usd12))
#         #         volume_24h_formatted12 = "{:.2f}".format(float(volume_24h12)) if float(
#         #             volume_24h12) < 1000 else shorten_number(float(volume_24h12))
#         #         emoji12 = '🔴' if float(price_change12) < 0 else '🟢'
#         #         updated_text12 = f'🌍 1 ALL = ${price12}  •  {emoji12}{price_change12}%\n\nLiquidity: ${liq_formatted12}  •  Volume 24h: ${volume_24h_formatted12}\n\nMarket Cap: ${fdv_usd_formatted12}'
#         #         article_content12 = types.InputTextMessageContent(message_text=updated_text12)
#         #         keyboard = types.InlineKeyboardMarkup()
#         #         buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/ALL")
#         #         refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_all")
#         #         keyboard.add(buy_button)
#         #         keyboard.add(refresh_button)
#         #         thumb_url12 = 'https://cache.tonapi.io/imgproxy/ej4mgAlS-D3rfXMetcy_ygpoxGraqfGx1liRXHHfaRA/rs:fill:200:200:1/g:no/aHR0cHM6Ly9naXRodWIuY29tL0FMTHRvbnRva2VuL0FMTC9ibG9iL21haW4vSU1HXzA4NDkucG5nP3Jhdz10cnVl.webp'  # Replace with the actual image URL
#         #
#         #         r12 = types.InlineQueryResultArticle(
#         #             id='12',
#         #             title='Курс 🌍 ALL в 💲USD',
#         #             description=f'🌍 1 ALL = ${price12}\nMarket Cap: ${fdv_usd_formatted12}',
#         #             input_message_content=article_content12,
#         #             thumbnail_url=thumb_url12,
#         #             reply_markup=keyboard
#         #         )
#         #         results.append(r12)
#         #
#         # # Corrected formatting for HYDRA token
#         # if price13 and fdv_usd13:
#         #     if not error13 and not api_error13:
#         #         liq_formatted13 = shorten_number(float(liquidity13))
#         #         fdv_usd_formatted13 = shorten_number(float(fdv_usd13))
#         #         volume_24h_formatted13 = "{:.2f}".format(float(volume_24h13)) if float(
#         #             volume_24h13) < 1000 else shorten_number(float(volume_24h13))
#         #         emoji13 = '🔴' if float(price_change13) < 0 else '🟢'
#         #         updated_text13 = f'🌿 1 HYDRA = ${price13}  •  {emoji13}{price_change13}%\n\nLiquidity: ${liq_formatted13}  •  Volume 24h: ${volume_24h_formatted13}\n\nMarket Cap: ${fdv_usd_formatted13}'
#         #         article_content13 = types.InputTextMessageContent(message_text=updated_text13)
#         #         keyboard = types.InlineKeyboardMarkup()
#         #         buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/HYDRA")
#         #         refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_hydra")
#         #         keyboard.add(buy_button)
#         #         keyboard.add(refresh_button)
#         #         thumb_url13 = 'https://cache.tonapi.io/imgproxy/gBmKmfWmjkjuH6uKqFT6_icGxp7LjBdBFOhusJcze2g/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1NoYWRvd1RpL3Rva2VuX3NvbnlhL21haW4vTE9HT19yNTZfMjU2LnBuZw.webp'  # Replace with the actual image URL
#         #
#         #         r13 = types.InlineQueryResultArticle(
#         #                 id='13',
#         #                 title='Курс 🌿 HYDRA в 💲USD',
#         #                 description=f'🌿 1 HYDRA = ${price13}\nMarket Cap: ${fdv_usd_formatted13}',
#         #                 input_message_content=article_content13,
#         #                 thumbnail_url=thumb_url13,
#         #                 reply_markup=keyboard
#         #             )
#         #         results.append(r13)
#         #
#         # price14, error14 = fetch_rcat_price_from_api()
#         # fdv_usd14, volume_24h14, liquidity14, price_change14, api_error14 = fetch_rcat_data(
#         #     'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAHBPL5Q51kQWMtItT3buuaDz0s_Bq4kN174-RKtlqOu07o/pools?page=1')
#         #
#         # # Data for EXC token
#         # price15, error15 = fetch_exc_price_from_api()
#         # fdv_usd15, volume_24h15, liquidity15, price_change15, api_error15 = fetch_exc_data(
#         #     'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC-A0ZHiAliPJ6LYQQZ6x2WRJC0aHEmJ_OMG6pidb5ASpIY/pools?page=1')
#         #
#         # # Handling and object creation for RCAT token
#         # if price14 and fdv_usd14:
#         #     if not error14 and not api_error14:
#         #         liq_formatted14 = shorten_number(float(liquidity14))
#         #         fdv_usd_formatted14 = shorten_number(float(fdv_usd14))
#         #         volume_24h_formatted14 = "{:.2f}".format(float(volume_24h14)) if float(
#         #             volume_24h14) < 1000 else shorten_number(float(volume_24h14))
#         #         emoji14 = '🔴' if float(price_change14) < 0 else '🟢'
#         #         updated_text14 = f'🐱 1 RCAT = ${price14}  •  {emoji14}{price_change14}%\n\nLiquidity: ${liq_formatted14}  •  Volume 24h: ${volume_24h_formatted14}\n\nMarket Cap: ${fdv_usd_formatted14}'
#         #         thumb_url14 = 'https://cache.tonapi.io/imgproxy/E0tHp4UgFPL5YNMU8LY7bTYnFujWgYZnCC_svoBCw5c/rs:fill:200:200:1/g:no/aHR0cHM6Ly9naXRodWIuY29tL01la3JpemthL3d3dy9ibG9iL21haW4vJUQwJUJBJUQwJUJFJUQxJTgxJUQwJUJDJUQwJUJFJUQwJUJBJUQwJUJFJUQxJTgyLnBuZz9yYXc9dHJ1ZQ.webp'  # Insert the actual image URL for RCAT
#         #         article_content14 = types.InputTextMessageContent(message_text=updated_text14)
#         #         keyboard = types.InlineKeyboardMarkup()
#         #         buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/RCAT")
#         #         refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_rcat")
#         #         keyboard.add(buy_button)
#         #         keyboard.add(refresh_button)
#         #     # Replace with the actual image URL
#         #
#         #         r14 = types.InlineQueryResultArticle(
#         #                 id='14',
#         #                 title='Курс 🐱 RCAT в 💲USD',
#         #                 description=f'🐱 1 RCAT = ${price14}\nMarket Cap: ${fdv_usd_formatted14}',
#         #                 input_message_content=article_content14,
#         #                 thumbnail_url=thumb_url14,
#         #                 reply_markup=keyboard
#         #             )
#         #
#         #         results.append(r14)
#         #
#         # # Handling and object creation for EXC token
#         # if price15 and fdv_usd15:
#         #     if not error15 and not api_error15:
#         #         liq_formatted15 = shorten_number(float(liquidity15))
#         #         fdv_usd_formatted15 = shorten_number(float(fdv_usd15))
#         #         volume_24h_formatted15 = "{:.2f}".format(float(volume_24h15)) if float(
#         #             volume_24h15) < 1000 else shorten_number(float(volume_24h15))
#         #         emoji15 = '🔴' if float(price_change15) < 0 else '🟢'
#         #         updated_text15 = f'🟡 1 EXC = ${price15}  •  {emoji15}{price_change15}%\n\nLiquidity: ${liq_formatted15}  •  Volume 24h: ${volume_24h_formatted15}\n\nMarket Cap: ${fdv_usd_formatted15}'
#         #         article_content15 = types.InputTextMessageContent(message_text=updated_text15)
#         #         keyboard = types.InlineKeyboardMarkup()
#         #         buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EXC")
#         #         refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_exc")
#         #         keyboard.add(buy_button)
#         #         keyboard.add(refresh_button)
#         #         thumb_url15 = 'https://cache.tonapi.io/imgproxy/76gMaetUvg36DeKDwosjjMIR-5X3R3m2eUoOVh4ybJE/rs:fill:200:200:1/g:no/aHR0cHM6Ly94b21hLm1vbnN0ZXIvZXgucG5n.webp'  # Replace with the actual image URL
#         #
#         #         r15 = types.InlineQueryResultArticle(
#         #                 id='15',
#         #                 title='Курс 🟡 EXC в 💲USD',
#         #                 description=f'🟡 1 EXC = ${price15}\nMarket Cap: ${fdv_usd_formatted15}',
#         #                 input_message_content=article_content15,
#         #                 thumbnail_url=thumb_url15,
#         #                 reply_markup=keyboard
#         #             )
#         #         results.append(r15)
#
#         price16, error16 = fetch_scale_price_from_api()
#         fdv_usd16, volume_24h16, liquidity16, price_change16, api_error16 = fetch_scale_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE/pools?page=1')
#
#         # Handling and object creation for SCALE token
#         if price16 and fdv_usd16:
#             if not error16 and not api_error16:
#                 liq_formatted16 = shorten_number(float(liquidity16))
#                 fdv_usd_formatted16 = shorten_number(float(fdv_usd16))
#                 volume_24h_formatted16 = "{:.2f}".format(float(volume_24h16)) if float(
#                     volume_24h16) < 1000 else shorten_number(float(volume_24h16))
#                 emoji16 = '🔴' if float(price_change16) < 0 else '🟢'
#                 updated_text16 = f'🔷 1 SCALE = ${price16}  •  {emoji16}{price_change16}%\n\nLiquidity: ${liq_formatted16}  •  Volume 24h: ${volume_24h_formatted16}\n\nMarket Cap: ${fdv_usd_formatted16}'
#                 thumb_url16 = 'https://cache.tonapi.io/imgproxy/5NPQb4dU02LiwsCpR9kW4hesLuqZwd5VRQXNC-K80bw/rs:fill:200:200:1/g:no/aXBmczovL1FtU01pWHNaWU1lZndyVFEzUDZIbkRRYUNwZWNTNEVXTHBnS0s1RVgxRzhpQTg.webp'  # Replace with the actual image URL
#                 article_content16 = types.InputTextMessageContent(message_text=updated_text16)
#                 keyboard = types.InlineKeyboardMarkup()
#                 buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SCALE")
#                 refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_scale")
#                 keyboard.add(buy_button)
#                 keyboard.add(refresh_button)
#                 r16 = types.InlineQueryResultArticle(
#                     id='16',
#                     title='Курс 🔷 SCALE в 💲USD',
#                     description=f'🔷 1 SCALE = ${price16}\nMarket Cap: ${fdv_usd_formatted16}',
#                     input_message_content=article_content16,
#                     thumbnail_url=thumb_url16,
#                     reply_markup=keyboard
#                 )
#                 results.append(r16)
#
#         # Data fetching for STON token
#         price17, error17 = fetch_ston_price_from_api()
#         fdv_usd17, volume_24h17, liquidity17, price_change17, api_error17 = fetch_ston_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO/pools?page=1')
#
#         # Handling and object creation for STON token
#         if price17 and fdv_usd17:
#             if not error17 and not api_error17:
#                 liq_formatted17 = shorten_number(float(liquidity17))
#                 fdv_usd_formatted17 = shorten_number(float(fdv_usd17))
#                 volume_24h_formatted17 = "{:.2f}".format(float(volume_24h17)) if float(
#                     volume_24h17) < 1000 else shorten_number(float(volume_24h17))
#                 emoji17 = '🔴' if float(price_change17) < 0 else '🟢'
#                 updated_text17 = f'🔵 1 STON = ${price17}  •  {emoji17}{price_change17}%\n\nLiquidity: ${liq_formatted17}  •  Volume 24h: ${volume_24h_formatted17}\n\nMarket Cap: ${fdv_usd_formatted17}'
#                 thumb_url17 = 'https://cache.tonapi.io/imgproxy/u6g-Eo01CQbP5ugIlzQUZEzM3DsU6ixZ7Z8wwJ2r_4g/rs:fill:200:200:1/g:no/aHR0cHM6Ly9zdGF0aWMuc3Rvbi5maS9sb2dvL3N0b25fc3ltYm9sLnBuZw.webp'
#                 article_content17 = types.InputTextMessageContent(message_text=updated_text17)
#                 keyboard = types.InlineKeyboardMarkup()
#                 buy_button = types.InlineKeyboardButton(text="STON.fi",
#                                                         url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=STON")
#                 refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_ston")
#                 keyboard.add(buy_button)
#                 keyboard.add(refresh_button)
#                 r17 = types.InlineQueryResultArticle(
#                     id='17',
#                     title='Курс 🔵 STON в 💲USD',
#                     description=f'🔵 1 STON = ${price17}\nMarket Cap: ${fdv_usd_formatted17}',
#                     input_message_content=article_content17,
#                     thumbnail_url=thumb_url17,
#                     reply_markup=keyboard
#                 )
#                 results.append(r17)
#
#         price18, error18 = fetch_arbuz_price_from_api()
#         fdv_usd18, volume_24h18, liquidity18, price_change18, api_error18 = fetch_arbuz_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAM2KWDp9lN0YvxvfSbI0ryjBXwM70rakpNIHbuETatRWA1/pools?page=1')
#
#         if price18 and fdv_usd18:
#             if not error18 and not api_error18:
#                 liq_formatted18 = shorten_number(float(liquidity18))
#                 fdv_usd_formatted18 = shorten_number(float(fdv_usd18))
#                 volume_24h_formatted18 = "{:.2f}".format(float(volume_24h18)) if float(
#                     volume_24h18) < 1000 else shorten_number(float(volume_24h18))
#                 emoji18 = '🔴' if float(price_change18) < 0 else '🟢'
#                 updated_text18 = f'🍉 1 ARBUZ = ${price18}  •  {emoji18}{price_change18}%\n\nLiquidity: ${liq_formatted18}  •  Volume 24h: ${volume_24h_formatted18}\n\nMarket Cap: ${fdv_usd_formatted18}'
#                 thumb_url18 = 'https://cache.tonapi.io/imgproxy/HxPeXiiX4pF3QFOJCnpmcEO8scn3vZsMstfXySfK5oI/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLnBvc3RpbWcuY2MvWEpnVmY3cGIvYXJiLnBuZw.webp'
#                 article_content18 = types.InputTextMessageContent(message_text=updated_text18)
#                 keyboard = types.InlineKeyboardMarkup()
#                 buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/ARBUZ")
#                 buy2_button = types.InlineKeyboardButton(text="STON.fi",
#                                                          url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=ARBUZ")
#                 refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_arbuz")
#                 keyboard.add(buy1_button, buy2_button)
#                 keyboard.add(refresh_button)
#                 r18 = types.InlineQueryResultArticle(
#                     id='18',
#                     title='Курс 🍉 ARBUZ в 💲USD',
#                     description=f'🍉 1 ARBUZ = ${price18}\nMarket Cap: ${fdv_usd_formatted18}',
#                     input_message_content=article_content18,
#                     thumbnail_url=thumb_url18,
#                     reply_markup=keyboard
#                 )
#                 results.append(r18)
#
#         price19, error19 = fetch_hmstr_price_from_api()
#         fdv_usd19, volume_24h19, liquidity19, price_change19, api_error19 = fetch_hmstr_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBam5RuB3inYXsUlamTIEqu-tNy5NmX4FBLAcZe_360eWWE/pools?page=1')
#
#         if price19 and fdv_usd19:
#             if not error19 and not api_error19:
#                 liq_formatted19 = shorten_number(float(liquidity19))
#                 fdv_usd_formatted19 = shorten_number(float(fdv_usd19))
#                 volume_24h_formatted19 = "{:.2f}".format(float(volume_24h19)) if float(
#                     volume_24h19) < 1000 else shorten_number(float(volume_24h19))
#                 emoji19 = '🔴' if float(price_change19) < 0 else '🟢'
#                 updated_text19 = f'🐹 1 HMSTR = ${price19}  •  {emoji19}{price_change19}%\n\nLiquidity: ${liq_formatted19}  •  Volume 24h: ${volume_24h_formatted19}\n\nMarket Cap: ${fdv_usd_formatted19}'
#                 article_content19 = types.InputTextMessageContent(message_text=updated_text19)
#                 keyboard = types.InlineKeyboardMarkup()
#                 buy_button = types.InlineKeyboardButton(text="DeDust",
#                                                         url="https://dedust.io/swap/TON/EQBam5RuB3inYXsUlamTIEqu-tNy5NmX4FBLAcZe_360eWWE")
#                 refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_hmstr")
#                 keyboard.add(buy_button)
#                 keyboard.add(refresh_button)
#                 thumb_url19 = 'https://cache.tonapi.io/imgproxy/U5TqEi9pA0tLtTLekAzSFIPwnzgxkDoZgBWRQHUfk0E/rs:fill:200:200:1/g:no/aHR0cHM6Ly9naXRodWIuY29tL2xvbHpoYW1zdGVyL3dlYnNpdGUvYmxvYi9tYWluL0ZyYW1lJTIwMTNsb2dvJTIwVE1DJTIwMygxKS5wbmc_cmF3PXRydWU.webp'  # Replace with the actual image URL
#
#                 r19 = types.InlineQueryResultArticle(
#                     id='19',
#                     title='Курс 🐹 HMSTR в 💲USD',
#                     description=f'🐹 1 HMSTR = ${price19}\nMarket Cap: ${fdv_usd_formatted19}',
#                     input_message_content=article_content19,
#                     thumbnail_url=thumb_url19,
#                     reply_markup=keyboard
#                 )
#                 results.append(r19)
#
#         price20, error20 = fetch_scam_price_from_api()
#         fdv_usd20, volume_24h20, liquidity20, price_change20, api_error20 = fetch_scam_data(
#             'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC52I3c2rmZpUav0LrU6q7wuXoTmhOInvaFhKjZ6QuC5tV5/pools?page=1')
#
#         if price20 and fdv_usd20:
#             if not error20 and not api_error20:
#                 liq_formatted20 = shorten_number(float(liquidity20))
#                 fdv_usd_formatted20 = shorten_number(float(fdv_usd20))
#                 volume_24h_formatted20 = "{:.2f}".format(float(volume_24h20)) if float(
#                     volume_24h20) < 1000 else shorten_number(float(volume_24h20))
#                 emoji20 = '🔴' if float(price_change20) < 0 else '🟢'
#                 updated_text20 = f'⛔️ 1 SCAM = ${price20}  •  {emoji20}{price_change20}%\n\nLiquidity: {liq_formatted20}  •  Volume 24h: {volume_24h_formatted20}\n\nMarket Cap: {fdv_usd_formatted20}'
#                 article_content20 = types.InputTextMessageContent(message_text=updated_text20)
#                 keyboard = types.InlineKeyboardMarkup()
#                 buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SCAM")
#                 refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_scam")
#                 keyboard.add(buy_button)
#                 keyboard.add(refresh_button)
#                 thumb_url20 = 'https://cache.tonapi.io/imgproxy/SmaTNb9sdPZSmMQR7qc06s_q2gU8xc3ZhD6UaJNTs0c/rs:fill:200:200:1/g:no/aHR0cHM6Ly9jZG4uam9pbmNvbW11bml0eS54eXovdG9rZW4vc2NhbS5wbmc.webp'  # Replace with the actual image URL
#
#                 r20 = types.InlineQueryResultArticle(
#                     id='20',
#                     title='Курс ⛔️ SCAM в 💲USD',
#                     description=f'⛔️ 1 SCAM = ${price20}\nMarket Cap: ${fdv_usd_formatted20}',
#                     input_message_content=article_content20,
#                     thumbnail_url=thumb_url20,
#                     reply_markup=keyboard
#                 )
#                 results.append(r20)
#
#         bot.answer_inline_query(inline_query.id, results)
#
#     except Exception as e:
#         print(f"Unhandled exception: {e}")

def fetch_crypto_price(url, class_name):
    # Fetch the crypto price from the given URL
    try:
        response = requests.get(url)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            price_span = soup.find('span', class_=class_name)
            if price_span:
                return price_span.text.strip(), None  # Return price and no error
            else:
                return None, "Could not find the price on the page. The page structure may have changed."
        else:
            return None, f"Failed to fetch data from the URL. Status Code: {response.status_code}"
    except requests.RequestException as e:
        return None, f"Network error occurred: {e}"


def fetch_crypto_data(url):
    try:
        response = requests.get(url)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Находим элемент с ценой
            price_element = soup.find('span', class_='sc-f70bb44c-0 jxpCgO base-text')
            price = price_element.text.strip() if price_element else None

            # Находим элемент с процентом изменения цены
            change_element = soup.find('p', class_='sc-4984dd93-0 sc-58c82cf9-1 fwNMDM')
            change = change_element.text.strip() if change_element else None

            return price, change, None
        else:
            return None, None, f"Failed to fetch data from the URL. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, f"Error occurred while fetching data from the URL: {e}"

def fetch_token_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            fdv_usd = data['data'][0]['attributes']['fdv_usd']
            price_change_percentage_h24 = data['data'][0]['attributes']['price_change_percentage']['h24']
            return fdv_usd, price_change_percentage_h24, None
        else:
            return None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, f"Error occurred while fetching data from the API: {e}"


@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price')
def refresh_price_callback(call):
    try:
        url = 'https://coinmarketcap.com/currencies/toncoin/'
        class_name = 'sc-f70bb44c-0 jxpCgO base-text'  # This class name may need updating
        api_url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c/pools?page=1'

        price, error = fetch_crypto_price(url, class_name)
        fdv_usd, price_change, api_error = fetch_token_data(api_url)

        if price and fdv_usd:  # Check if both prices are fetched successfully
            fdv_usd_formatted = '{:,.0f}'.format(float(fdv_usd))
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'💎 1 TON = {price}  •  {emoji}{price_change}%\n\nMarket Cap: ${fdv_usd_formatted}'

            # Add refresh button to the updated text
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price")
            keyboard = types.InlineKeyboardMarkup().add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                # If call.message is None, it means it's not a message from inline mode
                # We'll try to edit the message sent via inline query result ID
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    # If inline_query_message_id is also None, just answer with a new message
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")


@bot.inline_handler(func=lambda query: query.query.lower() == 'ton')
def query_text(inline_query):
    try:
        url = 'https://coinmarketcap.com/currencies/toncoin/'
        class_name = 'sc-f70bb44c-0 jxpCgO base-text'  # This class name may need updating
        api_url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c/pools?page=1'

        price, error = fetch_crypto_price(url, class_name)
        fdv_usd, price_change, api_error = fetch_token_data(api_url)

        if price and fdv_usd:  # Check if both prices are fetched successfully
            fdv_usd_formatted = '{:,.0f}'.format(float(fdv_usd))
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'💎 1 TON = {price}  •  {emoji}{price_change}%\n\nMarket Cap: ${fdv_usd_formatted}'

            thumb_url = 'https://danil1110.github.io/NFTcollcetion/TonImg.png'  # Replace with your actual thumbnail URL
            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price")
            keyboard = types.InlineKeyboardMarkup().add(refresh_button)
            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 💎 TON в 💲USD',
                description=f'💎 1 TON = {price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])



    except Exception as e:
        print(f"Unhandled exception: {e}")

""" ~~~ """

def fetch_crypto_price_lky():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCyDhcASwIm8-eVVTzMEESYAeQ7ettasfuGXUG1tkDwVJbc'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None  # Return price and no error
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)
def fetch_lky_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'LKY / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for LKY / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

# Обработчик запроса inline-запросов с ключевым словом 'lky'
@bot.inline_handler(func=lambda query: query.query.lower() == 'lky')
def query_text(inline_query):
    try:
        price, error = fetch_crypto_price_lky()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_lky_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCyDhcASwIm8-eVVTzMEESYAeQ7ettasfuGXUG1tkDwVJbc/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🍀 1 LKY = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/LKY")
            buy2_button = types.InlineKeyboardButton(text="STON.fi", url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=LKY")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_lky")
            keyboard.add(buy1_button, buy2_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/4DGuXDEqF18fzPL9cNlSuT5DFwoa1PKx-SjWJGWZpj8/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLmliYi5jby9YN3d2RDFQL01lYW5pbmctb2YtYS1Gb3VyLWxlYWYtQ2xvdmVyLVNpZ2h0aW5nLTIuanBn.webp'

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🍀 LKY в 💲USD',
                description=f'🍀 1 LKY = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Обработчик нажатия кнопки обновления цены LKY
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_lky')
def refresh_price_lky_callback(call):
    try:
        price, error = fetch_crypto_price_lky()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_lky_data('https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCyDhcASwIm8-eVVTzMEESYAeQ7ettasfuGXUG1tkDwVJbc/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🍀 1 LKY = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/LKY")
            buy2_button = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=LKY")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_lky")
            keyboard.add(buy1_button, buy2_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_inft_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAEfUNvB01k3khyyMJeQu6Y609TOPtm_-Mn0-12NJb4SXwR'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None  # Возвращаем цену в виде строки
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_inft_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'INFT / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for INFT / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'inft')
def query_text(inline_query):
    try:
        price, error = fetch_inft_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_inft_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAEfUNvB01k3khyyMJeQu6Y609TOPtm_-Mn0-12NJb4SXwR/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'♾️ 1 INFT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EQAEfUNvB01k3khyyMJeQu6Y609TOPtm_-Mn0-12NJb4SXwR")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_inft")
            keyboard.add(buy1_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/Pj8Zn7cD2mRcQ4_5RR3FIJN_sYn8KwYzcJIXy1PCi2A/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pbWFnZXVwLnJ1L2ltZzIyNy80NzY1NDc1L2ltZ18yMDI0MDMxNV8wNzE0MzhfODg1LmpwZw.webp'  # Замените на реальный URL изображения

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс ♾️ INFT в 💲USD',
                description=f'♾️ 1 INFT = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Обработчик нажатия кнопки обновления цены LKY
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_inft')
def refresh_price_inft_callback(call):
    try:
        price, error = fetch_inft_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_inft_data('https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAEfUNvB01k3khyyMJeQu6Y609TOPtm_-Mn0-12NJb4SXwR/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'♾️ 1 INFT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EQAEfUNvB01k3khyyMJeQu6Y609TOPtm_-Mn0-12NJb4SXwR")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_inft")
            keyboard.add(buy1_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_tribe_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCcXKwYGCCZnzQj9vwwg8Y-F3d8H7cow-Mwgj8pTFruBfP8'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None  # Возвращаем цену в виде строки
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_tribe_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'TRIBE / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for TRIBE / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'tribe')
def query_text(inline_query):
    try:
        price, error = fetch_tribe_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_tribe_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCcXKwYGCCZnzQj9vwwg8Y-F3d8H7cow-Mwgj8pTFruBfP8/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'👨‍👨‍👧‍👦 1 TRIBE = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/TRIBE")
            buy2_button = types.InlineKeyboardButton(text="STON.fi", url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=TRIBE")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_tribe")
            keyboard.add(buy1_button, buy2_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/C1CXpOhWuoQmDIlthqD9pLvFnpGdJGWcL8MywIH02J8/rs:fill:200:200:1/g:no/aHR0cHM6Ly9iYWZ5YmVpYXpia2oyNnJrdTZyZXIzaDJybGhwcGFoc25xbmVjNXllbmJyem0yNjYydWdzdWRzZWxxYS5pcGZzLnczcy5saW5rL3RyaWJldG9uMjU2LnBuZw.webp'  # Замените на реальный URL изображения

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 👨‍👨‍👧‍👦 TRIBE в 💲USD',
                description=f'👨‍👨‍👧‍👦 1 TRIBE = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Обработчик нажатия кнопки обновления цены LKY
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_tribe')
def refresh_price_lky_callback(call):
    try:
        price, error = fetch_tribe_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_tribe_data('https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCcXKwYGCCZnzQj9vwwg8Y-F3d8H7cow-Mwgj8pTFruBfP8/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'👨‍👨‍👧‍👦 1 TRIBE = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/TRIBE")
            buy2_button = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=TRIBE")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_tribe")
            keyboard.add(buy1_button, buy2_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

""" ~~~ """

def fetch_stbl_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD5ty5IxV3HECEY1bbbdd7rNNY-ZcA-pAIGQXyyRZRED9v3'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None  # Возвращаем цену в виде строки
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_stbl_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'STBL / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for STBL / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"


@bot.inline_handler(func=lambda query: query.query.lower() == 'stbl')
def query_text(inline_query):
    try:
        price, error = fetch_stbl_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_stbl_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD5ty5IxV3HECEY1bbbdd7rNNY-ZcA-pAIGQXyyRZRED9v3/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🏅 1 STBL = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/STBL")
            buy2_button = types.InlineKeyboardButton(text="STON.fi", url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=STBL")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_stbl")
            keyboard.add(buy1_button, buy2_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/t-4hk54FgHpwh0ErqRSIJWyJNIMeF-9v5V2t8omKAHo/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLmliYi5jby9IWWNzaHF2L3N0YmwtMjU2LnBuZw.webp'  # Замените на реальный URL изображения

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🏅 STBL в 💲USD',
                description=f'🏅 1 STBL = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")


# Handler for the price refresh button for STBL
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_stbl')
def refresh_price_stbl_callback(call):
    try:
        price, error = fetch_stbl_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_stbl_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD5ty5IxV3HECEY1bbbdd7rNNY-ZcA-pAIGQXyyRZRED9v3/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🏅 1 STBL = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/STBL")
            buy2_button = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=STBL")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_stbl")
            keyboard.add(buy1_button, buy2_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_unic_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQB2lbt2s_jdUW3OoUIb7-9RoK2UeGXmgC7BnOwgK6P_JTrm'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_unic_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'UNIC / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for UNIC / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"


@bot.inline_handler(func=lambda query: query.query.lower() == 'unic')
def query_text(inline_query):
    try:
        price, error = fetch_unic_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_unic_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQB2lbt2s_jdUW3OoUIb7-9RoK2UeGXmgC7BnOwgK6P_JTrm/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🦄 1 UNIC = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/UNIC")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_unic")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/UvPP-mdqRFu2diEOk2ztWog_Xz5TRm08-kxZdvHyEh0/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLmliYi5jby8wck5nQ2R0L3VuaWMyNTZ4MjU2LnBuZw.webp'  # Замените на реальный URL изображения

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🦄 UNIC в 💲USD',
                description=f'🦄 1 UNIC = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")


# Handler for the price refresh button for UNIC
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_unic')
def refresh_price_unic_callback(call):
    try:
        price, error = fetch_unic_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_unic_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQB2lbt2s_jdUW3OoUIb7-9RoK2UeGXmgC7BnOwgK6P_JTrm/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🦄 1 UNIC = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/UNIC")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_unic")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_ivs_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQACGPrFHWCy9QmeFXPqvZflyoeBb5grVQxAaucF0hNd1sEs'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_ivs_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'IVS / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for IVS / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'ivs')
def query_text(inline_query):
    try:
        price, error = fetch_ivs_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_ivs_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQACGPrFHWCy9QmeFXPqvZflyoeBb5grVQxAaucF0hNd1sEs/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'⭐ 1 IVS = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/IVS")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_ivs")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/_T8MQV5nrm3xlePtrP8UiAJKJ6VGFNSVld37YqCYYQ0/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1N0YWxpbkZvdW5kYXRpb24vSW1hZ2VzL21haW4vU3RhbGluTG9nby5wbmc.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс ⭐ IVS в 💲USD',
                description=f'⭐ 1 IVS = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for IVS
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_ivs')
def refresh_price_ivs_callback(call):
    try:
        price, error = fetch_ivs_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_ivs_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQACGPrFHWCy9QmeFXPqvZflyoeBb5grVQxAaucF0hNd1sEs/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'⭐ 1 IVS = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/IVS")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_ivs")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_bolt_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD0vdSA_NedR9uvbgN9EikRX-suesDxGeFg69XQMavfLqIw'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_bolt_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'BOLT / TON 1%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for BOLT / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'bolt')
def query_text(inline_query):
    try:
        price, error = fetch_bolt_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_bolt_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD0vdSA_NedR9uvbgN9EikRX-suesDxGeFg69XQMavfLqIw/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔩 1 BOLT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/BOLT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_bolt")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/05DkTmM2Eu4YZX-ED0eQpRS8U1q7SbD3o1GC5r5ZTBw/rs:fill:200:200:1/g:no/aHR0cHM6Ly9jbG91ZGZsYXJlLWlwZnMuY29tL2lwZnMvUW1YNDdkb2RVZzFhY1hveFlEVUxXVE5mU2hYUlc1dUhyQ21vS1NVTlI5eEtRdw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🔩 BOLT в 💲USD',
                description=f'🔩 1 BOLT = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for BOLT
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_bolt')
def refresh_price_bolt_callback(call):
    try:
        price, error = fetch_bolt_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_bolt_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD0vdSA_NedR9uvbgN9EikRX-suesDxGeFg69XQMavfLqIw/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔩 1 BOLT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/BOLT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_bolt")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_dfc_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD26zcd6Cqpz7WyLKVH8x_cD6D7tBrom6hKcycv8L8hV0GP'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_dfc_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'DFC / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for DFC / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'dfc')
def query_text(inline_query):
    try:
        price, error = fetch_dfc_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_dfc_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD26zcd6Cqpz7WyLKVH8x_cD6D7tBrom6hKcycv8L8hV0GP/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔎 1 DFC = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DFC")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi", url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=DFC")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_dfc")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/TENmVD1ZlCwI7F4dyM9k6PPyLzMrd7rZHIAyeom79SA/rs:fill:200:200:1/g:no/aHR0cHM6Ly90YW4tdG91Z2gtc2x1Zy0zNTEubXlwaW5hdGEuY2xvdWQvaXBmcy9RbVhRb2pKVVB2a0dDQ2VSOVF1OFd3bWNaRjFnTERZMjhlcExMaFBZdkR5OFRr.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🔎 DFC в 💲USD',
                description=f'🔎 1 DFC = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for DFC
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_dfc')
def refresh_price_dfc_callback(call):
    try:
        price, error = fetch_dfc_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_dfc_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD26zcd6Cqpz7WyLKVH8x_cD6D7tBrom6hKcycv8L8hV0GP/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔎 1 DFC = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DFC")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=DFC")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_dfc")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                              reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_gram_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC47093oX5Xhb0xuk2lCr2RhS8rj-vul61u4W2UH5ORmG_O'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_gram_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'GRAM / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for GRAM / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'gram')
def query_text(inline_query):
    try:
        price, error = fetch_gram_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_gram_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC47093oX5Xhb0xuk2lCr2RhS8rj-vul61u4W2UH5ORmG_O/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'◼️ 1 GRAM = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/GRAM")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi", url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=GRAM")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_gram")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/lNoY3YdNeBug53ixjK6hxT6XIX3_xoIYNqv-ykIQ1Aw/rs:fill:200:200:1/g:no/aHR0cHM6Ly9ncmFtY29pbi5vcmcvaW1nL2ljb24ucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс ◼️ GRAM в 💲USD',
                description=f'◼️ 1 GRAM = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for GRAM
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_gram')
def refresh_price_gram_callback(call):
    try:
        price, error = fetch_gram_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_gram_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC47093oX5Xhb0xuk2lCr2RhS8rj-vul61u4W2UH5ORmG_O/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'◼️ 1 GRAM = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/GRAM")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=GRAM")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_gram")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_dinja_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQByLZOaBbpr9EwNonXKEfkkZL1viNsYHezxw5CVK4Bh0zEb'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_dinja_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'DINJA / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for DINJA / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'dinja')
def query_text(inline_query):
    try:
        price, error = fetch_dinja_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_dinja_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQByLZOaBbpr9EwNonXKEfkkZL1viNsYHezxw5CVK4Bh0zEb/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🍈 1 DINJA = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DINJA")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_dinja")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/efWWgdJgqeiju2tCSsIeme0Aug1mA1PtaGjfWe8Qnys/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1dhdmVzVGlwQm90L0RJTkpBL21haW4vRElOSkEucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🍈 DINJA в 💲USD',
                description=f'🍈 1 DINJA = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for DINJA
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_dinja')
def refresh_price_dinja_callback(call):
    try:
        price, error = fetch_dinja_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_dinja_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQByLZOaBbpr9EwNonXKEfkkZL1viNsYHezxw5CVK4Bh0zEb/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🍈 1 DINJA = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DINJA")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_dinja")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_all_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDlnVo-6abJzyHlU8uB7pRjE7OIKt4HTTDPG4hfwOf5jTPg'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_all_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'ALL / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for ALL / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'all')
def query_text(inline_query):
    try:
        price, error = fetch_all_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_all_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDlnVo-6abJzyHlU8uB7pRjE7OIKt4HTTDPG4hfwOf5jTPg/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🌍 1 ALL = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/ALL")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_all")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/ej4mgAlS-D3rfXMetcy_ygpoxGraqfGx1liRXHHfaRA/rs:fill:200:200:1/g:no/aHR0cHM6Ly9naXRodWIuY29tL0FMTHRvbnRva2VuL0FMTC9ibG9iL21haW4vSU1HXzA4NDkucG5nP3Jhdz10cnVl.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🌍 ALL в 💲USD',
                description=f'🌍 1 ALL = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for ALL
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_all')
def refresh_price_all_callback(call):
    try:
        price, error = fetch_all_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_all_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDlnVo-6abJzyHlU8uB7pRjE7OIKt4HTTDPG4hfwOf5jTPg/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🌍 1 ALL = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/ALL")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_all")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_hydra_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD4P32U10snNoIavoq6cYPTQR82ewAjO20epigrWRAup54_'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_hydra_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'HYDRA / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for HYDRA / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'hydra')
def query_text(inline_query):
    try:
        price, error = fetch_hydra_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_hydra_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD4P32U10snNoIavoq6cYPTQR82ewAjO20epigrWRAup54_/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🌿 1 HYDRA = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/HYDRA")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_hydra")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/gBmKmfWmjkjuH6uKqFT6_icGxp7LjBdBFOhusJcze2g/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1NoYWRvd1RpL3Rva2VuX3NvbnlhL21haW4vTE9HT19yNTZfMjU2LnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🌿 HYDRA в 💲USD',
                description=f'🌿 1 HYDRA = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for HYDRA
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_hydra')
def refresh_price_hydra_callback(call):
    try:
        price, error = fetch_hydra_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_hydra_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD4P32U10snNoIavoq6cYPTQR82ewAjO20epigrWRAup54_/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🌿 1 HYDRA = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/HYDRA")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_hydra")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_rcat_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAHBPL5Q51kQWMtItT3buuaDz0s_Bq4kN174-RKtlqOu07o'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_rcat_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'RCat / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for RCAT / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'rcat')
def query_text(inline_query):
    try:
        price, error = fetch_rcat_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_rcat_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAHBPL5Q51kQWMtItT3buuaDz0s_Bq4kN174-RKtlqOu07o/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐱 1 RCAT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/RCAT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_rcat")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/E0tHp4UgFPL5YNMU8LY7bTYnFujWgYZnCC_svoBCw5c/rs:fill:200:200:1/g:no/aHR0cHM6Ly9naXRodWIuY29tL01la3JpemthL3d3dy9ibG9iL21haW4vJUQwJUJBJUQwJUJFJUQxJTgxJUQwJUJDJUQwJUJFJUQwJUJBJUQwJUJFJUQxJTgyLnBuZz9yYXc9dHJ1ZQ.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🐱 RCAT в 💲USD',
                description=f'🐱 1 RCAT = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for RCAT
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_rcat')
def refresh_price_rcat_callback(call):
    try:
        price, error = fetch_rcat_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_rcat_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAHBPL5Q51kQWMtItT3buuaDz0s_Bq4kN174-RKtlqOu07o/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐱 1 RCAT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/RCAT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_rcat")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_exc_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC-A0ZHiAliPJ6LYQQZ6x2WRJC0aHEmJ_OMG6pidb5ASpIY'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_exc_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'EXC / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for EXC / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'exc')
def query_text(inline_query):
    try:
        price, error = fetch_exc_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_exc_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC-A0ZHiAliPJ6LYQQZ6x2WRJC0aHEmJ_OMG6pidb5ASpIY/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🟡 1 EXC = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EXC")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_exc")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/76gMaetUvg36DeKDwosjjMIR-5X3R3m2eUoOVh4ybJE/rs:fill:200:200:1/g:no/aHR0cHM6Ly94b21hLm1vbnN0ZXIvZXgucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🟡 EXC в 💲USD',
                description=f'🟡 1 EXC = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for EXC
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_exc')
def refresh_price_exc_callback(call):
    try:
        price, error = fetch_exc_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_exc_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC-A0ZHiAliPJ6LYQQZ6x2WRJC0aHEmJ_OMG6pidb5ASpIY/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🟡 1 EXC = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EXC")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_exc")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_scale_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_scale_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'SCALE / TON 1%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for SCALE / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'scale')
def query_text(inline_query):
    try:
        price, error = fetch_scale_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_scale_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔷 1 SCALE = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SCALE")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_scale")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/5NPQb4dU02LiwsCpR9kW4hesLuqZwd5VRQXNC-K80bw/rs:fill:200:200:1/g:no/aXBmczovL1FtU01pWHNaWU1lZndyVFEzUDZIbkRRYUNwZWNTNEVXTHBnS0s1RVgxRzhpQTg.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🔷 SCALE в 💲USD',
                description=f'🔷 1 SCALE = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for SCALE
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_scale')
def refresh_price_scale_callback(call):
    try:
        price, error = fetch_scale_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_scale_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔷 1 SCALE = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SCALE")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_scale")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_ston_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_ston_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'STON / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for STON / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'ston')
def query_text(inline_query):
    try:
        price, error = fetch_ston_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_ston_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔵 1 STON = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="STON.fi",
                                                    url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=STON")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_ston")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/u6g-Eo01CQbP5ugIlzQUZEzM3DsU6ixZ7Z8wwJ2r_4g/rs:fill:200:200:1/g:no/aHR0cHM6Ly9zdGF0aWMuc3Rvbi5maS9sb2dvL3N0b25fc3ltYm9sLnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🔵 STON в 💲USD',
                description=f'🔵 1 STON = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for STON
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_ston')
def refresh_price_ston_callback(call):
    try:
        price, error = fetch_ston_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_ston_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔵 1 STON = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="STON.fi", url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=STON")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_ston")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_arbuz_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAM2KWDp9lN0YvxvfSbI0ryjBXwM70rakpNIHbuETatRWA1'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_arbuz_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'ARBUZ / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for ARBUZ / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'arbuz')
def query_text(inline_query):
    try:
        price, error = fetch_arbuz_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_arbuz_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAM2KWDp9lN0YvxvfSbI0ryjBXwM70rakpNIHbuETatRWA1/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🍉 1 ARBUZ = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/ARBUZ")
            buy2_button = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=ARBUZ")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_arbuz")
            keyboard.add(buy1_button, buy2_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/HxPeXiiX4pF3QFOJCnpmcEO8scn3vZsMstfXySfK5oI/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLnBvc3RpbWcuY2MvWEpnVmY3cGIvYXJiLnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🍉 ARBUZ в 💲USD',
                description=f'🍉 1 ARBUZ = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for ARBUZ
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_arbuz')
def refresh_price_arbuz_callback(call):
    try:
        price, error = fetch_arbuz_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_arbuz_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAM2KWDp9lN0YvxvfSbI0ryjBXwM70rakpNIHbuETatRWA1/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🍉 1 ARBUZ = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy1_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/ARBUZ")
            buy2_button = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=ARBUZ")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_arbuz")
            keyboard.add(buy1_button, buy2_button)
            keyboard.add(refresh_button)
            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_hmstr_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBam5RuB3inYXsUlamTIEqu-tNy5NmX4FBLAcZe_360eWWE'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_hmstr_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'HMSTR / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for HMSTR / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'hmstr')
def query_text(inline_query):
    try:
        price, error = fetch_hmstr_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_hmstr_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBam5RuB3inYXsUlamTIEqu-tNy5NmX4FBLAcZe_360eWWE/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐹 1 HMSTR = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EQBam5RuB3inYXsUlamTIEqu-tNy5NmX4FBLAcZe_360eWWE")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_hmstr")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/U5TqEi9pA0tLtTLekAzSFIPwnzgxkDoZgBWRQHUfk0E/rs:fill:200:200:1/g:no/aHR0cHM6Ly9naXRodWIuY29tL2xvbHpoYW1zdGVyL3dlYnNpdGUvYmxvYi9tYWluL0ZyYW1lJTIwMTNsb2dvJTIwVE1DJTIwMygxKS5wbmc_cmF3PXRydWU.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🐹 HMSTR в 💲USD',
                description=f'🐹 1 HMSTR = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for HMSTR
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_hmstr')
def refresh_price_hmstr_callback(call):
    try:
        price, error = fetch_hmstr_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_hmstr_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBam5RuB3inYXsUlamTIEqu-tNy5NmX4FBLAcZe_360eWWE/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐹 1 HMSTR = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EQBam5RuB3inYXsUlamTIEqu-tNy5NmX4FBLAcZe_360eWWE")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_hmstr")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_scam_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC52I3c2rmZpUav0LrU6q7wuXoTmhOInvaFhKjZ6QuC5tV5'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_scam_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'SCAM / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for SCAM / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'scam')
def query_text(inline_query):
    try:
        price, error = fetch_scam_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_scam_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC52I3c2rmZpUav0LrU6q7wuXoTmhOInvaFhKjZ6QuC5tV5/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'⛔️ 1 SCAM = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SCAM")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_scam")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/SmaTNb9sdPZSmMQR7qc06s_q2gU8xc3ZhD6UaJNTs0c/rs:fill:200:200:1/g:no/aHR0cHM6Ly9jZG4uam9pbmNvbW11bml0eS54eXovdG9rZW4vc2NhbS5wbmc.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс ⛔️ SCAM в 💲USD',
                description=f'⛔️ 1 SCAM = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for SCAM
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_scam')
def refresh_price_scam_callback(call):
    try:
        price, error = fetch_scam_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_scam_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC52I3c2rmZpUav0LrU6q7wuXoTmhOInvaFhKjZ6QuC5tV5/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'⛔️ 1 SCAM = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SCAM")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_scam")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")


def fetch_kingy_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC-tdRjjoYMz3MXKW4pj95bNZgvRyWwZ23Jix3ph7guvHxJ'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_kingy_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'KINGY / TON 1%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for KINGY / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'kingy')
def query_text(inline_query):
    try:
        price, error = fetch_kingy_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_kingy_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC-tdRjjoYMz3MXKW4pj95bNZgvRyWwZ23Jix3ph7guvHxJ/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🦘 1 KINGY = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/KINGY")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=KINGY")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_gram")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/yFer2GtQ4Jz-GbW8FIGD_69r8GH7GNkHvYZGy3fikJ0/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLmliYi5jby9GYlRDS1JQL2xvZ290b2tlbmtpbmd5LnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🦘 KINGY в 💲USD',
                description=f'🦘 1 KINGY = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for KINGY
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_kingy')
def refresh_price_kingy_callback(call):
    try:
        price, error = fetch_kingy_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_kingy_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQC-tdRjjoYMz3MXKW4pj95bNZgvRyWwZ23Jix3ph7guvHxJ/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🦘 1 KINGY = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/KINGY")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=KINGY")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_gram")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_up_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCvaf0JMrv6BOvPpAgee08uQM_uRpUd__fhA7Nm8twzvbE_'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_up_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'UP / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for UP / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'up')
def query_text(inline_query):
    try:
        price, error = fetch_up_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_up_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCvaf0JMrv6BOvPpAgee08uQM_uRpUd__fhA7Nm8twzvbE_/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔼 1 UP = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/UP")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=UP")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_up")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/os0pSC99m71BN9D8jcEP_78ZkvjE4qc3PlXK9mYQizM/rs:fill:200:200:1/g:no/aHR0cHM6Ly9wdWJsaWMtbWljcm9jb3NtLnMzLWFwLXNvdXRoZWFzdC0xLmFtYXpvbmF3cy5jb20vZHJvcHNoYXJlLzE3MDI1NDM2MjkvVVAtaWNvbi5wbmc.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🔼 UP в 💲USD',
                description=f'🔼 1 UP = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for UP
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_up')
def refresh_price_up_callback(call):
    try:
        price, error = fetch_up_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_up_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCvaf0JMrv6BOvPpAgee08uQM_uRpUd__fhA7Nm8twzvbE_/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔼 1 UP = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/UP")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=UP")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_up")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_fish_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQATcUc69sGSCCMSadsVUKdGwM1BMKS-HKCWGPk60xZGgwsK'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_fish_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'FISH / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for FISH / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'fish')
def query_text(inline_query):
    try:
        price, error = fetch_fish_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_fish_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQATcUc69sGSCCMSadsVUKdGwM1BMKS-HKCWGPk60xZGgwsK/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐟 1 FISH = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/FISH")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=FISH")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_fish")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/64G--D3N6KARJulIFT18L3fSWk-6ZtXPBWDG_vZl9i8/rs:fill:200:200:1/g:no/aHR0cHM6Ly93d3cudG9uZmlzaC5pby9CTFVFQ09JTjIucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🐟 FISH в 💲USD',
                description=f'🐟 1 FISH = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for FISH
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_fish')
def refresh_price_fish_callback(call):
    try:
        price, error = fetch_fish_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_fish_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQATcUc69sGSCCMSadsVUKdGwM1BMKS-HKCWGPk60xZGgwsK/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐟 1 FISH = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/FISH")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=FISH")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_fish")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_tpet_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAmQGimKRrSHDLllvdUdeDsX1CszGy_SPgNNN8wE2ihIwnP'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_tpet_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'TPET / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for TPET / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'tpet')
def query_text(inline_query):
    try:
        price, error = fetch_tpet_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_tpet_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAmQGimKRrSHDLllvdUdeDsX1CszGy_SPgNNN8wE2ihIwnP/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🦮 1 TPET = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            #buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/TPET")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=TPET")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_tpet")
            keyboard.add(buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/JOixKjeOYVStjB-SKTHDK9n-VI06hwTNBw3fl1PRJEs/rs:fill:200:200:1/g:no/aHR0cHM6Ly93d3cudG9uZmlzaC5pby9pbWFnZXMvQkxVRV9UX0NPSU4yLnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🦮 TPET в 💲USD',
                description=f'🦮 1 TPET = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for TPET
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_tpet')
def refresh_price_tpet_callback(call):
    try:
        price, error = fetch_tpet_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_tpet_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAmQGimKRrSHDLllvdUdeDsX1CszGy_SPgNNN8wE2ihIwnP/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🦮 1 TPET = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            #buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/TPET")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=TPET")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_tpet")
            keyboard.add(buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_fnz_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDCJL0iQHofcBBvFBHdVG233Ri2V4kCNFgfRT-gqAd3Oc86'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_fnz_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'FNZ / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for FNZ / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'fnz')
def query_text(inline_query):
    try:
        price, error = fetch_fnz_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_fnz_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDCJL0iQHofcBBvFBHdVG233Ri2V4kCNFgfRT-gqAd3Oc86/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔥 1 FNZ = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=FNZ")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_fnz")
            keyboard.add(buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/4ygLYy5lzNAwdBhSb0GBKCNxNlps2I_mzMTt5JUTmto/rs:fill:200:200:1/g:no/aHR0cHM6Ly9jZG4uZmFuei5lZS90b2tlbnMvZm56NTAwLnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🔥 FNZ в 💲USD',
                description=f'🔥 1 FNZ = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for FNZ
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_fnz')
def refresh_price_fnz_callback(call):
    try:
        price, error = fetch_fnz_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_fnz_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDCJL0iQHofcBBvFBHdVG233Ri2V4kCNFgfRT-gqAd3Oc86/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🔥 1 FNZ = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=FNZ")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_fnz")
            keyboard.add(buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_punk_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCdpz6QhJtDtm2s9-krV2ygl45Pwl-KJJCV1-XrP-Xuuxoq'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_punk_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'PUNK / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for PUNK / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'punk')
def query_text(inline_query):
    try:
        price, error = fetch_punk_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_punk_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCdpz6QhJtDtm2s9-krV2ygl45Pwl-KJJCV1-XrP-Xuuxoq/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🅿️ 1 PUNK = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=PUNK")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_punk")
            keyboard.add(buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/mehFYlb1uDc1wa0RaKBQPCAKxBBiPcwIHHXd0-u4Ejo/rs:fill:200:200:1/g:no/aHR0cHM6Ly9wdW5rLW1ldGF2ZXJzZS5mcmExLmRpZ2l0YWxvY2VhbnNwYWNlcy5jb20vbG9nby9wdW5rLnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🅿️ PUNK в 💲USD',
                description=f'🅿️ 1 PUNK = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for PUNK
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_punk')
def refresh_price_punk_callback(call):
    try:
        price, error = fetch_punk_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_punk_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCdpz6QhJtDtm2s9-krV2ygl45Pwl-KJJCV1-XrP-Xuuxoq/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🅿️'

            updated_text = f'🅿️ 1 PUNK = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=PUNK")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_punk")
            keyboard.add(buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_jetton_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAQXlWJvGbbFfE8F3oS8s87lIgdovS455IsWFaRdmJetTon'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_jetton_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'JETTON / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for JETTON / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'jetton')
def query_text(inline_query):
    try:
        price, error = fetch_jetton_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_jetton_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAQXlWJvGbbFfE8F3oS8s87lIgdovS455IsWFaRdmJetTon/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🪙 1 JETTON = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/JETTON")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=JETTON")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_jetton")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/VF6OeC8JlQ19hW2ecTD4t-mm5K9kmU8PvlFvqmwOj3s/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0pldFRvbi1Cb3QvSmV0VG9uL21haW4vamV0dG9uLTI1Ni5wbmc.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🪙 JETTON в 💲USD',
                description=f'🪙 1 JETTON = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for JETTON
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_jetton')
def refresh_price_jetton_callback(call):
    try:
        price, error = fetch_jetton_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_jetton_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAQXlWJvGbbFfE8F3oS8s87lIgdovS455IsWFaRdmJetTon/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🪙 1 JETTON = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/JETTON")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=JETTON")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_jetton")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_ult_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAQU1jz5ShPaS9mxvI6NVBvwBl5_1b7YDemAzMCluDUMPgT'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_ult_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'ULT / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for ULT / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'ult')
def query_text(inline_query):
    try:
        price, error = fetch_ult_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_ult_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAQU1jz5ShPaS9mxvI6NVBvwBl5_1b7YDemAzMCluDUMPgT/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🤖 1 ULT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=EQAQU1jz5ShPaS9mxvI6NVBvwBl5_1b7YDemAzMCluDUMPgT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_ult")
            keyboard.add(buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/UBbHN3UenYl_K10QdvWqVhqUZG3U4CpniDC0tNzD2o0/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1RtYjY4L3VsdHJvbi9tYWluL0lNR18yMDI0MDEwMV8xODE4NDcucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🤖 ULT в 💲USD',
                description=f'🤖 1 ULT = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for ULT
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_ult')
def refresh_price_ult_callback(call):
    try:
        price, error = fetch_ult_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_ult_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAQU1jz5ShPaS9mxvI6NVBvwBl5_1b7YDemAzMCluDUMPgT/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🤖 1 ULT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=EQAQU1jz5ShPaS9mxvI6NVBvwBl5_1b7YDemAzMCluDUMPgT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_ult")
            keyboard.add(buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_sock_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQARb2CYeCT73K-a_cWXycgbcWlleEx4fq4RCbZ7cWBtPN8s'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_sock_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'SOCK / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for SOCK / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'sock')
def query_text(inline_query):
    try:
        price, error = fetch_sock_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_sock_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQARb2CYeCT73K-a_cWXycgbcWlleEx4fq4RCbZ7cWBtPN8s/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🧦 1 SOCK = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SOCK")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_sock")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/IEpjyAiJiVJBxCuu1J02VCOnyc4WlCgAIMmxexuRZ-U/rs:fill:200:200:1/g:no/aHR0cHM6Ly9sdGRmb3RvLnJ1L2ltYWdlcy8yMDI0LzAzLzI2L2ltZ29ubGluZS1jb20tdWEtUmVzaXplLXo5b0Z5Y3l2b01kZEkucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🧦 SOCK в 💲USD',
                description=f'🧦 1 SOCK = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for SOCK
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_sock')
def refresh_price_sock_callback(call):
    try:
        price, error = fetch_sock_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_sock_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQARb2CYeCT73K-a_cWXycgbcWlleEx4fq4RCbZ7cWBtPN8s/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🧦 1 SOCK = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SOCK")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_sock")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_statham_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBHcVEoIwZ22GifL7BtVTGkzJKLQoC-rmqV6_nj7SR-hL2P'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_statham_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'STATHAM / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for STATHAM / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'statham')
def query_text(inline_query):
    try:
        price, error = fetch_statham_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_statham_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBHcVEoIwZ22GifL7BtVTGkzJKLQoC-rmqV6_nj7SR-hL2P/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'👊 1 STATHAM = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/STATHAM")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_statham")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://assets.dedust.io/images/statham.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 👊 STATHAM в 💲USD',
                description=f'👊 1 STATHAM = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for STATHAM
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_statham')
def refresh_price_statham_callback(call):
    try:
        price, error = fetch_statham_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_statham_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBHcVEoIwZ22GifL7BtVTGkzJKLQoC-rmqV6_nj7SR-hL2P/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'👊 1 STATHAM = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/STATHAM")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_statham")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_slow_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDK3ReFkb6L3uE3GmMDJaxWby4PA_UYGClgFfJuXY52-TOK'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_slow_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'SLOW / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for SLOW / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'slow')
def query_text(inline_query):
    try:
        price, error = fetch_slow_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_slow_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDK3ReFkb6L3uE3GmMDJaxWby4PA_UYGClgFfJuXY52-TOK/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐌 1 SLOW = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SLOW")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_slow")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/WY9-K95SFd5HN-3NVdvsaxX2wljNgkCVvzKbHab4PX4/rs:fill:200:200:1/g:no/aHR0cHM6Ly9zbG93LWludmVzdG1lbnRzLmdpdGh1Yi5pby93ZWJzaXRlL2xvZ28ucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🐌 SLOW в 💲USD',
                description=f'🐌 1 SLOW = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for SLOW
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_slow')
def refresh_price_slow_callback(call):
    try:
        price, error = fetch_slow_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_slow_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDK3ReFkb6L3uE3GmMDJaxWby4PA_UYGClgFfJuXY52-TOK/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐌 1 SLOW = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/SLOW")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_slow")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_anon_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDv-yr41_CZ2urg2gfegVfa44PDPjIK9F-MilEDKDUIhlwZ'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_anon_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'ANON / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for ANON / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'anon')
def query_text(inline_query):
    try:
        price, error = fetch_anon_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_anon_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDv-yr41_CZ2urg2gfegVfa44PDPjIK9F-MilEDKDUIhlwZ/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🎱 1 ANON = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/ANON")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=ANON")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_anon")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/3nkA_bafJ5kaFjWLLfiCc2TZ5vVZYeqzu4dtNwdKkCs/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLmliYi5jby8wTVpnODd6L0lNRy04Mzk5LnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🎱 ANON в 💲USD',
                description=f'🎱 1 ANON = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for ANON
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_anon')
def refresh_price_anon_callback(call):
    try:
        price, error = fetch_anon_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_anon_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDv-yr41_CZ2urg2gfegVfa44PDPjIK9F-MilEDKDUIhlwZ/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🎱 1 ANON = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/ANON")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=ANON")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_anon")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_redo_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBZ_cafPyDr5KUTs0aNxh0ZTDhkpEZONmLJA2SNGlLm4Cko'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_redo_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'REDO / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for REDO / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'redo')
def query_text(inline_query):
    try:
        price, error = fetch_redo_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_redo_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBZ_cafPyDr5KUTs0aNxh0ZTDhkpEZONmLJA2SNGlLm4Cko/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐶 1 REDO = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/REDO")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=REDO")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_redo")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/R-9iv8csp1jZ9ymWn4dvcnYC_z3seU2dCrDdU2whQn4/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1Jlc2lzdGFuY2UtRG9nL3Jlc2lzdGFuY2UtZG9nL21haW4vcmVzaXN0YW5jZS1kb2cud2VicA.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🐶 REDO в 💲USD',
                description=f'🐶 1 REDO = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for REDO
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_redo')
def refresh_price_redo_callback(call):
    try:
        price, error = fetch_redo_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_redo_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBZ_cafPyDr5KUTs0aNxh0ZTDhkpEZONmLJA2SNGlLm4Cko/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐶 1 REDO = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/REDO")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=REDO")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_redo")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_duck_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBTcytZjdZwFLj6TO7CeGvn4aMmqXvbX-nODiApbd011gT3'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_duck_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'DUCK / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for DUCK / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'duck')
def query_text(inline_query):
    try:
        price, error = fetch_duck_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_duck_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBTcytZjdZwFLj6TO7CeGvn4aMmqXvbX-nODiApbd011gT3/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🦆 1 DUCK = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DUCK")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=DUCK")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_duck")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/kxmx0kWpNNKRyoqkyETfLnR46K-uioZ3AkfPRb2a2zg/rs:fill:200:200:1/g:no/aHR0cHM6Ly9naXRodWIuY29tL0R1Y2tNaXplbC9EdWNrQ29pbi9ibG9iL21haW4vZHVjay5wbmc_cmF3PXRydWU.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🦆 DUCK в 💲USD',
                description=f'🦆 1 DUCK = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for DUCK
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_duck')
def refresh_price_duck_callback(call):
    try:
        price, error = fetch_duck_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_duck_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBTcytZjdZwFLj6TO7CeGvn4aMmqXvbX-nODiApbd011gT3/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🦆 1 DUCK = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DUCK")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=DUCK")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_duck")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_wnot_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCIXQn940RNcOk6GzSorRSiA9WZC9xUz-6lyhl6Ap6na2sh'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_wnot_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'wNOT / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for WNOT / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'wnot')
def query_text(inline_query):
    try:
        price, error = fetch_wnot_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_wnot_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCIXQn940RNcOk6GzSorRSiA9WZC9xUz-6lyhl6Ap6na2sh/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🧊 1 WNOT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=WNOT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_wnot")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/XekGaOII3AolQZlfOLHhvGuHEUuK2x4hlMMU1_z7NVU/rs:fill:200:200:1/g:no/aHR0cHM6Ly9zaGFyZGlmeS5hcHAvdG9rZW5zL25vdGNvaW4vaW1hZ2UucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🧊 WNOT в 💲USD',
                description=f'🧊 1 WNOT = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for WNOT
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_wnot')
def refresh_price_wnot_callback(call):
    try:
        price, error = fetch_wnot_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_wnot_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCIXQn940RNcOk6GzSorRSiA9WZC9xUz-6lyhl6Ap6na2sh/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🧊 1 WNOT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=WNOT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_wnot")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_mrdn_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCymLRXp1QYxZKek4CTInckB1ey5TkyAJQpPAlNetiO54Vt'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_mrdn_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'MRDN / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for MRDN / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'mrdn')
def query_text(inline_query):
    try:
        price, error = fetch_mrdn_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_mrdn_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCymLRXp1QYxZKek4CTInckB1ey5TkyAJQpPAlNetiO54Vt/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🧱 1 MRDN = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/MRDN")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=MRDN")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_mrdn")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/IESWHWz9kcghRi2Qvuz0TmeA_6doAMYVT39-lyxyLWc/rs:fill:200:200:1/g:no/aHR0cHM6Ly9taW5lLm1lcmlkaWFuLnd0Zi9jb2luX2ltYWdlLnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🧱 MRDN в 💲USD',
                description=f'🧱 1 MRDN = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for MRDN
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_mrdn')
def refresh_price_mrdn_callback(call):
    try:
        price, error = fetch_mrdn_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_mrdn_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQCymLRXp1QYxZKek4CTInckB1ey5TkyAJQpPAlNetiO54Vt/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🧱 1 MRDN = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/MRDN")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=MRDN")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_mrdn")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_pot_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDoziSttQZ96QJRxHRKdatCm5L9DRL9LKycXcjl8RPXZM0N'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_pot_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'POT / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for POT / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'pot')
def query_text(inline_query):
    try:
        price, error = fetch_pot_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_pot_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDoziSttQZ96QJRxHRKdatCm5L9DRL9LKycXcjl8RPXZM0N/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'💠 1 POT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/POT")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=POT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_pot")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/SUCI5Jvgaa7ee9oz9pBrGWZjkHqR7WH5tecJ9KnRN-E/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0phY2twb3QtdG9uL3BvdC1qZXR0b24vbWFpbi9sb2dvLnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 💠 POT в 💲USD',
                description=f'💠 1 POT = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for POT
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_pot')
def refresh_price_pot_callback(call):
    try:
        price, error = fetch_pot_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_pot_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQDoziSttQZ96QJRxHRKdatCm5L9DRL9LKycXcjl8RPXZM0N/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'💠 1 POT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/POT")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=POT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_pot")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_dra_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBE_P2bKO9dHGSwUhZbQv6va-YRuEWUEZuCv_iEXgO-psTz'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_dra_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'DRA / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for DRA / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'dra')
def query_text(inline_query):
    try:
        price, error = fetch_dra_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_dra_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBE_P2bKO9dHGSwUhZbQv6va-YRuEWUEZuCv_iEXgO-psTz/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐲 1 DRA = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DRA")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_dra")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/ttUyA6tvdItOGesEcrnQIjFsiUEnoPXFpmc1tnWIh_U/rs:fill:200:200:1/g:no/aHR0cHM6Ly9zYXZlLmZvbGxvd2RyYWdvbnMubW9uc3Rlci9kcmFjb2luL2RyYS5wbmc.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🐲 DRA в 💲USD',
                description=f'🐲 1 DRA = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for DRA
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_dra')
def refresh_price_dra_callback(call):
    try:
        price, error = fetch_dra_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_dra_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQBE_P2bKO9dHGSwUhZbQv6va-YRuEWUEZuCv_iEXgO-psTz/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🐲 1 DRA = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/DRA")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_dra")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_black_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAWq99UkPClHcxuqpVy_a1H0e13dfIPJlKeDDbqLFokKL2m'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_black_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'BLACK / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for BLACK / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'black')
def query_text(inline_query):
    try:
        price, error = fetch_black_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_black_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAWq99UkPClHcxuqpVy_a1H0e13dfIPJlKeDDbqLFokKL2m/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'♠️ 1 BLACK = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EQAWq99UkPClHcxuqpVy_a1H0e13dfIPJlKeDDbqLFokKL2m")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_black")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/3_FQAAbmwOCJrxUcV2sAxkX28vO4n7O2G6LABjuFMGk/rs:fill:200:200:1/g:no/aHR0cHM6Ly9pLmliYi5jby9YdDRxUk5OL1Bob3Rvcm9vbS0yMDI0MDMxNS0xMzUwMzcucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс ♠️ BLACK в 💲USD',
                description=f'♠️ 1 BLACK = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for BLACK
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_black')
def refresh_price_black_callback(call):
    try:
        price, error = fetch_black_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_black_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQAWq99UkPClHcxuqpVy_a1H0e13dfIPJlKeDDbqLFokKL2m/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'♠️ 1 BLACK = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EQAWq99UkPClHcxuqpVy_a1H0e13dfIPJlKeDDbqLFokKL2m")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_black")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_lifeyt_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD_KpO2-iFeHPT4dF0ur9E0iAFts2fwhpR2KjwAmYKpccvH'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_lifeyt_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'LIFEYT / TON 0.4%':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for LIFEYT / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'lifeyt')
def query_text(inline_query):
    try:
        price, error = fetch_lifeyt_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_lifeyt_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD_KpO2-iFeHPT4dF0ur9E0iAFts2fwhpR2KjwAmYKpccvH/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🧡 1 LIFEYT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/LIFEYT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_lifeyt")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/Fz3GRHANGoAK_hyEVwjDzJhgmu1g5StxsNFdgzuvFKQ/rs:fill:200:200:1/g:no/aHR0cHM6Ly9saWZleXQtc3RhcnQuZ2l0aHViLmlvL0pVL0BsaWZleXQucG5n.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🧡 LIFEYT в 💲USD',
                description=f'🧡 1 LIFEYT = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for LIFEYT
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_lifeyt')
def refresh_price_lifeyt_callback(call):
    try:
        price, error = fetch_lifeyt_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_lifeyt_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD_KpO2-iFeHPT4dF0ur9E0iAFts2fwhpR2KjwAmYKpccvH/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🧡 1 LIFEYT = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/LIFEYT")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_lifeyt")
            keyboard.add(buy_button)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")

def fetch_blck_price_from_api():
    url = 'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD-J6UqYQezuUm6SlPDnHwTxXqo4uHys_fle_zKvM5nYJkA'
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            price_usd = data['data']['attributes']['price_usd']
            return str(price_usd), None
        else:
            return None, "Failed to fetch data"
    except requests.RequestException as e:
        return None, str(e)

def fetch_blck_data(api_url):
    try:
        response = requests.get(api_url)
        if response.ok:
            data = response.json()
            pools = data['data']
            for pool in pools:
                if pool['attributes']['name'] == 'BLKC / TON':
                    volume_24h = pool['attributes']['volume_usd']['h24']
                    liquidity = pool['attributes']['reserve_in_usd']
                    fdv_usd = pool['attributes']['fdv_usd']
                    price_change_percentage_h24 = pool['attributes']['price_change_percentage']['h24']
                    return fdv_usd, volume_24h, liquidity, price_change_percentage_h24, None
            return None, None, None, None, "Could not find pool data for BLCK / TON"
        else:
            return None, None, None, None, f"Failed to fetch data from the API. Status Code: {response.status_code}"
    except Exception as e:
        return None, None, None, None, f"Error occurred while fetching data from the API: {e}"

@bot.inline_handler(func=lambda query: query.query.lower() == 'blkc')
def query_text(inline_query):
    try:
        price, error = fetch_blck_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_blck_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD-J6UqYQezuUm6SlPDnHwTxXqo4uHys_fle_zKvM5nYJkA/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🎩 1 BLKC = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EQD-J6UqYQezuUm6SlPDnHwTxXqo4uHys_fle_zKvM5nYJkA")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=EQD-J6UqYQezuUm6SlPDnHwTxXqo4uHys_fle_zKvM5nYJkA")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_blck")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            thumb_url = 'https://cache.tonapi.io/imgproxy/UPGN85w2GUkH26SgdNpnrzPLpUw2Rshulq9QMYnj2z8/rs:fill:200:200:1/g:no/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0JsYWNrSGF0Q29pbi9qZXR0b24vbWFzdGVyL2xvZ29fbGlnaHQyNTZ4MjU2LnBuZw.webp'  # Replace with the actual image URL

            article_content = types.InputTextMessageContent(
                message_text=updated_text
            )

            r = types.InlineQueryResultArticle(
                id='1',
                title='Курс 🎩 BLKC в 💲USD',
                description=f'🎩 1 BLCK = ${price}\nMarket Cap: ${fdv_usd_formatted}',
                input_message_content=article_content,
                thumbnail_url=thumb_url,
                reply_markup=keyboard
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Error: {error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

        elif api_error:
            r = types.InlineQueryResultArticle(
                id='1',
                title='Error',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"API Error: {api_error}"
                )
            )
            bot.answer_inline_query(inline_query.id, [r])

    except Exception as e:
        print(f"Unhandled exception: {e}")

# Handler for the price refresh button for BLCK
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_price_blkc')
def refresh_price_blck_callback(call):
    try:
        price, error = fetch_blck_price_from_api()
        fdv_usd, volume_24h, liquidity, price_change, api_error = fetch_blck_data(
            'https://api.geckoterminal.com/api/v2/networks/ton/tokens/EQD-J6UqYQezuUm6SlPDnHwTxXqo4uHys_fle_zKvM5nYJkA/pools?page=1')

        if price and fdv_usd and volume_24h and liquidity and price_change:
            liq_formatted = shorten_number(float(liquidity))
            fdv_usd_formatted = shorten_number(float(fdv_usd))
            volume_24h_formatted = ""  # Initialize with a default value
            if float(volume_24h) < 1000:
                volume_24h_formatted = "{:.2f}".format(float(volume_24h))
            else:
                volume_24h_formatted = shorten_number(
                    float(volume_24h))  # Assigning a value for cases where volume_24h >= 1000
            emoji = '🔴' if float(price_change) < 0 else '🟢'

            updated_text = f'🎩 1 BLKC = ${price}  •  {emoji}{price_change}%\n\nLiquidity: ${liq_formatted}  •  Volume 24h: ${volume_24h_formatted}\n\nMarket Cap: ${fdv_usd_formatted}'

            keyboard = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(text="DeDust", url="https://dedust.io/swap/TON/EQD-J6UqYQezuUm6SlPDnHwTxXqo4uHys_fle_zKvM5nYJkA")
            buy_button2 = types.InlineKeyboardButton(text="STON.fi",
                                                     url="https://app.ston.fi/swap?chartVisible=false&ft=TON&tt=EQD-J6UqYQezuUm6SlPDnHwTxXqo4uHys_fle_zKvM5nYJkA")
            refresh_button = types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_price_blck")
            keyboard.add(buy_button, buy_button2)
            keyboard.add(refresh_button)

            if call.message:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=updated_text, reply_markup=keyboard)
            else:
                inline_query_message_id = call.inline_message_id
                if inline_query_message_id:
                    bot.edit_message_text(inline_message_id=inline_query_message_id, text=updated_text,
                                          reply_markup=keyboard)
                else:
                    bot.answer_callback_query(call.id, text=updated_text)

        elif error:
            bot.answer_callback_query(call.id, text=f"Error: {error}", show_alert=True)
        elif api_error:
            bot.answer_callback_query(call.id, text=f"API Error: {api_error}", show_alert=True)

    except Exception as e:
        print(f"Unhandled exception: {e}")


def signal_handler(sig, frame):
    print('Вы нажали Ctrl+C. Остановка бота.')
    sys.exit(0)

def start_bot():
    print("Бот запущен.")
    while True:
        try:
            # Ваш код инициализации бота и вызова метода polling
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Произошло исключение: {e}")
            continue

# Добавляем обработчик сигнала Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Вызываем функцию для запуска бота
start_bot()