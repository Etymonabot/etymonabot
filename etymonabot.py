import os
import openai
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import BotCommand
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
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
    await message.reply("Привет! Я Etymonabot — бот для подготовки к олимпиаде по лингвистике.\n\nОтправь мне слово, и я объясню его морфемный состав и этимологию.\n\nПопробуй: /explain декабрь")

# Команда /explain
@dp.message_handler(commands=['explain'])
async def explain_word(message: types.Message):
    query = message.get_args()
    if not query:
        await message.reply("Пожалуйста, укажи слово после команды. Например: /explain декабрь")
        return

    await message.reply("🔎 Думаю над словом: " + query)

      try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — лингвист и преподаватель этимологии и морфологии в профильном гуманитарном вузе. "
                        "Отвечай глубоко, профессионально, как для студентов-филологов. "
                        "Для каждого слова делай полный разбор:\n"
                        "— морфемный состав (обозначь корень, суффиксы, приставки — если есть);\n"
                        "— этимологию: происхождение, путь заимствования (с указанием языков и форм);\n"
                        "— семантическое развитие и сдвиги значений;\n"
                        "— тип заимствования, если применимо (книжное, разговорное и т.д.);\n"
                        "— как минимум один академический источник (Фасмер, Клейн, TLFi, Duden и др.).\n"
                        "Пиши как лингвист-филолог, не упрощай."
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

# Обработка всех остальных сообщений
@dp.message_handler()
async def handle_text(message: types.Message):
    await message.reply("Чтобы узнать этимологию слова, используй команду /explain <слово>")

# Запуск бота и установка команд
async def on_startup(dp):
    await set_bot_commands(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

