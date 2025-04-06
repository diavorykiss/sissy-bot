import os
import logging
from flask import Flask, request
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.wsgi import WsgiToAsgi

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация Flask-приложения
app = Flask(__name__)

# Получение токена из переменных окружения (или напрямую, если вы его задаёте)
TOKEN = os.getenv("TELEGRAM_TOKEN", "7622812077:AAGz1Jiaq5IXdfyhqZO3i4aXeHs8EgCOksg")

# Инициализация Telegram Application
application = Application.builder().token(TOKEN).build()

# Функция для команды /start
async def start(update, context):
    logger.info(f"Получена команда /start от пользователя {update.effective_user.id}")
    # Создаём клавиатуру с кнопками
    keyboard = [
        [
            InlineKeyboardButton("Задания 📋", callback_data="tasks"),
            InlineKeyboardButton("Гипноз 🌀", callback_data="hypno"),
        ],
        [
            InlineKeyboardButton("Заработать очки 💎", callback_data="earn"),
            InlineKeyboardButton("Экстремальные задания 🔥", callback_data="extreme"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Отправляем сообщение с клавиатурой
    await update.message.reply_text(
        "На колени, сиси! 🙇 Я твоя Госпожа, ты моя кукла! Смотри на меня и подчиняйся! 👑",
        reply_markup=reply_markup
    )

# Функция для обработки нажатий на кнопки
async def button(update, context):
    query = update.callback_query
    await query.answer()
    logger.info(f"Пользователь {query.from_user.id} нажал кнопку: {query.data}")

    if query.data == "tasks":
        await query.message.reply_text("Вот твои задания, сиси! Выполняй! 📋")
    elif query.data == "hypno":
        await query.message.reply_text("Погружаемся в гипноз, сиси... 🌀")
    elif query.data == "earn":
        await query.message.reply_text("Зарабатывай очки, моя кукла! 💎")
    elif query.data == "extreme":
        await query.message.reply_text("Экстремальные задания для тебя, сиси! 🔥")

# Добавление обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

# Инициализация приложения
application.initialize()

# Установка вебхука при запуске
@app.before_first_request
async def set_webhook():
    webhook_url = f"https://sissy-bot.onrender.com/{TOKEN}"
    logger.info(f"Установка вебхука на {webhook_url}")
    await application.bot.set_webhook(webhook_url)

# Маршрут для вебхука
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    logger.info("Получен запрос вебхука")
    update = request.get_json()
    logger.info(f"Обработка обновления: {update['update_id']}")
    await application.process_update(update)
    return {"ok": True}

# Корневой маршрут для проверки
@app.route("/")
def index():
    logger.info("Получен запрос к корневому маршруту /")
    return "Бот запущен!"

# Обёртка Flask-приложения для совместимости с ASGI
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    # Для локальной разработки
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
