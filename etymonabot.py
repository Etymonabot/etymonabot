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
                    "content": """
Ты — эксперт по морфемике и этимологии русского языка.
Разбирай слово строго по современным правилам морфемного анализа:

— Учитывай только те морфемы, которые реально выделяются в современном русском языке (на базе школьной и вузовской грамматики).
— Если слово не делится на морфемы, прямо указывай: \"слово имеет цельную неразложимую основу\".
— Не выделяй суффиксы или приставки, которые не встречаются в других словах.
— Не придумывай морфемное членение по звуку, если оно не подтверждается современными грамматиками (например, в слове \"морковь\" корень — \"морковь\", а не \"морк-\").

После морфемного разбора кратко опиши этимологию: происхождение слова, путь заимствования (если есть), и сдвиги значений.

Пиши точно, лаконично и без избыточной лирики.
"""
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

# Cards data
cards_data = [
    {"number": 1, "latin": "unus", "greek": "heis (εἷς)", "examples": ["unison", "uniform", "universe"]},
    {"number": 2, "latin": "duo", "greek": "dyo (δύο)", "examples": ["duet", "dual", "duplicate"]},
    {"number": 3, "latin": "tres", "greek": "treis (τρεῖς)", "examples": ["triangle", "trio", "triple"]},
    {"number": 4, "latin": "quattuor", "greek": "tessares (τέσσαρες)", "examples": ["quartet", "quadrant", "tetrahedron"]},
    {"number": 5, "latin": "quinque", "greek": "pente (πέντε)", "examples": ["pentagon", "pentathlon", "quintet"]},
    {"number": 6, "latin": "sex", "greek": "hex (ἕξ)", "examples": ["hexagon", "sextet", "sextuple"]},
    {"number": 7, "latin": "septem", "greek": "hepta (ἑπτά)", "examples": ["September", "heptagon", "heptathlon"]},
    {"number": 8, "latin": "octo", "greek": "okto (ὀκτώ)", "examples": ["octopus", "octagon", "October"]},
    {"number": 9, "latin": "novem", "greek": "ennea (ἐννέα)", "examples": ["nonagon", "enneagram", "November"]},
    {"number": 10, "latin": "decem", "greek": "deka (δέκα)", "examples": ["decimal", "decade", "decagon"]},
    {"number": 11, "latin": "undecim", "greek": "hendeka (ἕνδεκα)", "examples": []},
    {"number": 12, "latin": "duodecim", "greek": "dodeka (δώδεκα)", "examples": ["dodecahedron"]},
    {"number": 13, "latin": "tredecim", "greek": "triskaideka (τρισκαίδεκα)", "examples": []},
    {"number": 14, "latin": "quattuordecim", "greek": "tetrakaideka (τετρακαιδέκα)", "examples": []},
    {"number": 15, "latin": "quindecim", "greek": "pentekaideka (πεντεκαιδέκα)", "examples": []},
    {"number": 16, "latin": "sedecim", "greek": "hexakaideka (ἑξακαιδέκα)", "examples": []},
    {"number": 17, "latin": "septendecim", "greek": "heptakaideka (ἑπτακαιδέκα)", "examples": []},
    {"number": 18, "latin": "duodeviginti", "greek": "oktokaideka (ὀκτωκαιδέκα)", "examples": []},
    {"number": 19, "latin": "undeviginti", "greek": "enneakaideka (ἐννεακαιδέκα)", "examples": []},
    {"number": 20, "latin": "viginti", "greek": "eikosi (εἴκοσι)", "examples": ["icosahedron"]},
    {"number": 30, "latin": "triginta", "greek": "triakonta (τριάκοντα)", "examples": []},
    {"number": 40, "latin": "quadraginta", "greek": "tessarakonta (τεσσαράκοντα)", "examples": []},
    {"number": 50, "latin": "quinquaginta", "greek": "pentekonta (πεντήκοντα)", "examples": []},
    {"number": 60, "latin": "sexaginta", "greek": "hexekonta (ἑξήκοντα)", "examples": []},
    {"number": 70, "latin": "septuaginta", "greek": "hebdomēkonta (ἑβδομήκοντα)", "examples": []},
    {"number": 80, "latin": "octoginta", "greek": "ogdoekonta (ὀγδοήκοντα)", "examples": []},
    {"number": 90, "latin": "nonaginta", "greek": "enenēkonta (ἐνενήκοντα)", "examples": []},
    {"number": 100, "latin": "centum", "greek": "hekaton (ἑκατόν)", "examples": ["percent", "hecatomb"]},
    {"number": 200, "latin": "ducenti", "greek": "diakosia (διακόσια)", "examples": []},
    {"number": 300, "latin": "trecenti", "greek": "triakosia (τριακόσια)", "examples": []},
    {"number": 400, "latin": "quadringenti", "greek": "tetrakosia (τετρακόσια)", "examples": []},
    {"number": 500, "latin": "quingenti", "greek": "pentakosia (πεντακόσια)", "examples": []},
    {"number": 600, "latin": "sescenti", "greek": "hexakosia (ἑξακόσια)", "examples": []},
    {"number": 700, "latin": "septingenti", "greek": "heptakosia (ἑπτακόσια)", "examples": []},
    {"number": 800, "latin": "octingenti", "greek": "oktakosia (ὀκτακόσια)", "examples": []},
    {"number": 900, "latin": "nongenti", "greek": "enneakosia (ἐννεακόσια)", "examples": []},
    {"number": 1000, "latin": "mille", "greek": "chilia (χίλια)", "examples": ["millennium", "millimeter"]}
]

# Для отслеживания прогресса по карточкам
user_card_index = {}

@dp.message_handler(commands=['cards'])
async def send_first_card(message: types.Message):
    user_card_index[message.from_user.id] = 0
    card = cards_data[0]
    await message.reply(format_card(card))

@dp.message_handler(commands=['next'])
async def send_next_card(message: types.Message):
    user_id = message.from_user.id
    index = user_card_index.get(user_id, 0) + 1
    if index < len(cards_data):
        user_card_index[user_id] = index
        await message.reply(format_card(cards_data[index]))
    else:
        await message.reply("🎉 Это была последняя карточка!")


def format_card(card):
    text = f"🔢 {card['number']}\n"
    text += f"🇱🇦 Латинский: {card['latin']}\n"
    text += f"🇬🇷 Греческий: {card['greek']}\n"
    if card['examples']:
        text += "\n📘 Примеры:\n"
        for ex in card['examples']:
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
