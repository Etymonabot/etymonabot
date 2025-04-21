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

# Устанавливаем команды для меню
async def set_bot_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "Приветствие и инструкция"),
        BotCommand("explain", "Объяснить слово"),
        BotCommand("cards", "Карточки: латинские и греческие числительные"),
        BotCommand("quiz", "Небольшая викторина по словам")
    ])

# Приветствие
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я Etymonabot — бот для подготовки к олимпиаде по лингвистике.\n\nНапиши команду /explain и я помогу разобрать любое слово.")

# FSM-состояние
class ExplainWord(StatesGroup):
    waiting_for_word = State()

# Команда /explain запускает диалог
@dp.message_handler(commands=['explain'])
async def start_explain(message: types.Message):
    await message.reply("Какое слово вы хотите разобрать?")
    await ExplainWord.waiting_for_word.set()

# Получение слова и анализ
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
                    "content": (
                        Ты — эксперт по морфемике и этимологии русского языка. 
Разбирай слово строго по современным правилам морфемного анализа:

— Учитывай только те морфемы, которые реально выделяются в современном русском языке (на базе школьной и вузовской грамматики).
— Если слово не делится на морфемы, прямо указывай: "слово имеет цельную неразложимую основу".
— Не выделяй суффиксы или приставки, которые не встречаются в других словах.
— Не придумывай морфемное членение по звуку, если оно не подтверждается современными грамматиками (например, в слове "морковь" корень — "морковь", а не "морк-").

После морфемного разбора кратко опиши этимологию: происхождение слова, путь заимствования (если есть), и сдвиги значений.

Пиши точно, лаконично и без избыточной лирики.
                    )
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

# Обработка остальных сообщений
@dp.message_handler()
async def handle_text(message: types.Message):
    await message.reply("Чтобы разобрать слово, напиши команду /explain")

# Запуск бота и установка команд
async def on_startup(dp):
    await set_bot_commands(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


