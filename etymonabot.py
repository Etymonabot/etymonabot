import os
import openai
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
openai.api_key = OPENAI_API_KEY

# FSM-состояние
class ExplainWord(StatesGroup):
    waiting_for_word = State()

@dp.message_handler(commands=['explain'])
async def start_explain(message: types.Message):
    await message.reply("Какое слово вы хотите разобрать?")
    await ExplainWord.waiting_for_word.set()

@dp.message_handler(state=ExplainWord.waiting_for_word)
async def explain_word_fsm(message: types.Message, state: FSMContext):
    query = message.text.strip()
    await message.reply("🔎 Думаю над словом: " + query)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — лингвист и преподаватель этимологии и морфологии в профильном гуманитарном вузе. Отвечай глубоко, профессионально, как для студентов-филологов. Для каждого слова делай полный разбор:

— морфемный состав (обозначь корень, суффиксы, приставки — если есть);
— этимологию: происхождение, путь заимствования (с указанием языков и форм);
— семантическое развитие и сдвиги значений;
— тип заимствования, если применимо (книжное, разговорное и т.д.);
— как минимум один академический источник (Фасмер, Клейн, TLFi, Duden и др.).

Пиши как лингвист-филолог, не упрощай.""
                },
                {
                    "role": "user",
                    "content": f"Сделай этимолого-морфемный разбор слова: {query}"
                }
            ]
        )
        explanation = response['choices'][0]['message']['content']
        await message.reply(explanation)
    except Exception as e:
        logging.error(e)
        await message.reply("Произошла ошибка при обработке запроса. Попробуй позже.")

    await state.finish()

cards_data = [
    {"number": 0, "latin": "nulla", "greek": "ouden", "examples": [], "examples_ru": [], "note": "Латинское 'nulla' — ничто"},
    {"number": 1, "latin": "unus", "greek": "heis", "examples": ["universe"], "examples_ru": ["унификация"]},
    {"number": 2, "latin": "duo", "greek": "dyo", "examples": ["dual"], "examples_ru": ["дуэт"]},
    {"number": 3, "latin": "tres", "greek": "treis", "examples": ["triangle"], "examples_ru": ["трио"]},
    {"number": 4, "latin": "quattuor", "greek": "tettares", "examples": ["quadrant"], "examples_ru": ["квадрант"]},
    {"number": 5, "latin": "quinque", "greek": "pente", "examples": ["pentagon"], "examples_ru": ["пентатлон"]},
    {"number": 6, "latin": "sex", "greek": "hex", "examples": ["sextet"], "examples_ru": ["гексада"]},
    {"number": 7, "latin": "septem", "greek": "hepta", "examples": ["September"], "examples_ru": ["гептодром"]},
    {"number": 8, "latin": "octo", "greek": "okto", "examples": ["octopus"], "examples_ru": ["октава"]},
    {"number": 9, "latin": "novem", "greek": "ennea", "examples": ["November"], "examples_ru": ["эннеагон"]},
    {"number": 10, "latin": "decem", "greek": "deka", "examples": ["decimal"], "examples_ru": ["декада"]}
]

# Для отслеживания прогресса по карточкам
user_card_index = {}
user_quiz_index = {}
user_quiz_score = {}

@dp.message_handler(commands=['quiz'])
async def send_quiz_intro(message: types.Message):
    user_id = message.from_user.id
    user_quiz_index[user_id] = 0
    user_quiz_score[user_id] = 0
    await message.reply("🧠 Викторина: назови число по латинскому и греческому написанию. Отправь цифру в ответ.")
    await send_quiz_card(message.chat.id, user_id)

async def send_first_card(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("0–10", callback_data="cards_0_10"),
        types.InlineKeyboardButton("10–20", callback_data="cards_10_20"),
    )
    keyboard.add(
        types.InlineKeyboardButton("20–100", callback_data="cards_20_100"),
        types.InlineKeyboardButton("100–1000", callback_data="cards_100_1000"),
    )
    await message.reply("Выбери диапазон карточек:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data and (c.data.startswith("cards_") or c.data == "back_to_menu"))
async def process_card_range(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    if data == "cards_0_10":
        user_card_index[user_id] = next(i for i, c in enumerate(cards_data) if c['number'] == 0)
    elif data == "cards_10_20":
        user_card_index[user_id] = next(i for i, c in enumerate(cards_data) if c['number'] == 10)
    elif data == "cards_20_100":
        user_card_index[user_id] = next(i for i, c in enumerate(cards_data) if c['number'] == 20)
    elif data == "cards_100_1000":
        user_card_index[user_id] = next(i for i, c in enumerate(cards_data) if c['number'] == 100)
    elif data == "back_to_menu":
        await send_first_card(callback_query.message)
        await callback_query.answer()
        return
    else:
        await callback_query.answer("Неверный диапазон")
        return

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔙 Назад к выбору диапазона", callback_data="back_to_menu"))
    await callback_query.message.answer(format_card(cards_data[user_card_index[user_id]]), reply_markup=keyboard)
    await callback_query.answer()

@dp.message_handler(commands=['next'])
async def send_next_card(message: types.Message):
    user_id = message.from_user.id
    index = user_card_index.get(user_id, 0) + 1
    if index < len(cards_data):
        user_card_index[user_id] = index
        await message.reply(format_card(cards_data[index]))
    else:
        await message.reply("🎉 Это была последняя карточка!")

async def send_quiz_card(chat_id, user_id):
    if user_quiz_index[user_id] >= len(cards_data):
        score = user_quiz_score[user_id]
        await bot.send_message(chat_id, f"🏁 Викторина окончена! Ты набрал {score} из {len(cards_data)}.")
        return
    card = cards_data[user_quiz_index[user_id]]
    text = (
        f"🇱🇦 Латинское: {card['latin']}\n"
        f"🇬🇷 Греческое: {card['greek']}\n\n"
        f"Сколько это? Введи цифру."
    )
    await bot.send_message(chat_id, text)

@dp.message_handler(lambda message: message.text.isdigit())
async def check_quiz_answer(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_quiz_index:
        return  # не в режиме викторины

    current_card = cards_data[user_quiz_index[user_id]]
    correct = str(current_card['number']) == message.text.strip()
    if correct:
        user_quiz_score[user_id] += 1
        await message.reply("✅ Верно!")
    else:
        await message.reply(f"❌ Неверно. Правильный ответ: {current_card['number']}")

    user_quiz_index[user_id] += 1
    await send_quiz_card(message.chat.id, user_id)

def format_card(card):
    text = f"🔢 {card['number']}\n"
    text += f"🇱🇦 Латинский: {card['latin']}\n"
    text += f"🇬🇷 Греческий: {card['greek']}\n"
    if card.get('note'):
        text += f"\n📙 Образование:\n{card['note']}\n"
    if card.get('examples'):
        text += "\n📘 Примеры на других языках:\n"
        for ex in card['examples']:
            text += f"• {ex}\n"
    if card.get('examples_ru'):
        text += "\n📗 Примеры на русском:\n"
        for ex in card['examples_ru']:
            text += f"• {ex}\n"
    text += "\n➡️ Напиши /next, чтобы продолжить"
    return text

# Запуск
async def on_startup(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "Приветствие и инструкция"),
        BotCommand("explain", "Объяснить слово"),
        BotCommand("cards", "Карточки: латинские и греческие числительные"),
        BotCommand("quiz", "Небольшая викторина по словам")
    ])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
