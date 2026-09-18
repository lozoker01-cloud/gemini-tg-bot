import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiohttp import web
from groq import AsyncGroq

# Получаем ключи из безопасных переменных окружения сервера
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Инициализируем бота и диспетчер
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Инициализируем асинхронный клиент Groq
client = AsyncGroq(api_key=GROQ_API_KEY)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я переведен на новые мощности и готов к работе.")

@dp.message()
async def handle_message(message: Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Отправляем текст пользователя в Groq
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message.text,
                }
            ],
            model="llama-3.3-70b-instant",
        )
        
        # Извлекаем текст ответа и отправляем без форматирования Markdown
        response_text = chat_completion.choices[0].message.content
        await message.answer(response_text)
        
    except Exception as e:
        await message.answer(f"Ошибка API: {e}")

# --- Заглушка веб-сервера для Render ---
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    # Запускаем одновременно веб-сервер и опрос Telegram
    await asyncio.gather(
        web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
