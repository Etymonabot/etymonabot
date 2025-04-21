import os
import openai
import logging
from aiogram import Bot, Dispatcher, executor, types
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

# Start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я Etymonabot — бот для подготовки к олимпиаде по лингвистике.\n\nОтправь мне слово, и я объясню его морфемный состав и этимологию.\n\nПопробуй: /explain декабрь")

# Explain command
@dp.message_handler(commands=['explain'])
async def explain_word(message: types.Message):
    query = message.get_args()
    if not query:
        await message.reply("Пожалуйста, укажи слово после команды. Например: /explain декабрь")
        return

    await message.reply("🔎 Думаю над словом: " + query)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — эксперт по морфологии и этимологии русского языка."},
                {"role": "user", "content": f"Объясни морфемный состав и этимологию слова '{query}' для старшеклассника, готовящегося к олимпиаде по лингвистике. Объясни просто, но точно."}
            ]
        )
        explanation = response['choices'][0]['message']['content']
        await message.reply(explanation)
    except Exception as e:
        logging.error(e)
        await message.reply("Произошла ошибка при обработке запроса. Попробуй позже.")

# Fallback handler for any text
@dp.message_handler()
async def handle_text(message: types.Message):
    await message.reply("Чтобы узнать этимологию слова, используй команду /explain <слово>")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
