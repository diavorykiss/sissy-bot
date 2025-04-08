import os
import sys
import logging
import random
import fcntl
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
TOKEN = os.getenv("BOT_TOKEN", "7622812077:AAGz1Jiaq5IXdfyhqZO3i4aXeHs8EgCOksg")
MEDIA_PATH = "media"

# Определение медиафайлов
media = {
    "start": ["start.jpg"],
    "task": [f"task_{i}.jpg" for i in range(1, 16)],
    "extreme": [f"extreme_{i}.jpg" for i in range(1, 12)],
    "earn": [f"earn_{i}.mp4" for i in range(1, 8)],
    "hypno": [f"hypno_{i}.gif" for i in range(1, 29)]
}

# Определение заданий (оставляем без изменений)
tasks = {
    "beginner": [
        ("Побрей ноги и стань гладкой девочкой! 🪒\nКак выполнить: Возьми бритву и пену для бритья, аккуратно сбрей все волосы с ног, чтобы они стали гладкими и мягкими, как у настоящей девочки. Нанеси увлажняющий крем с нежным ароматом, сделай фото своих ножек и отправь Госпоже с подписью 'Я начинаю становиться твоей девочкой, Госпожа!' ✨", "task_1.jpg"),
        # ... остальные задания ...
    ],
    "middle": [
        ("Накрась губы и стань кокетливой девочкой! 💄\nКак выполнить: Выбери ярко-розовую или красную помаду, аккуратно накрась губы, посмотри на себя в зеркале и улыбнись. Сделай селфи с надутыми губками, как настоящая девочка, и отправь Госпоже с подписью 'Я становлюсь кокетливой девочкой для тебя, Госпожа!' 😘", "task_6.jpg"),
        # ... остальные задания ...
    ],
    "advanced": [
        ("Надень платье и стань настоящей принцессой! 👗\nКак выполнить: Найди милое платье (например, розовое или с цветочным узором), надень его, добавь колготки и аксессуары (например, серёжки или браслет). Сделай полный макияж (помада, тени, румяна), сними видео, где ты крутишься и говоришь 'Я твоя принцесса, Госпожа!' и отправь его. 💃", "task_11.jpg"),
        # ... остальные задания ...
    ],
    "extreme": [
        ("Соси себя как шлюха! 🍆\nКак выполнить: Надень чулки и лифчик, попробуй достать ртом до своего члена, сними видео своих усилий и скажи 'Я твоя грязная сиси, Госпожа, посмотри на меня!' 🎥", "extreme_1.jpg"),
        # ... остальные задания ...
    ],
    "earn": [
        ("Стань послушной девочкой в отеле и заработай для Госпожи! 🏨\nКак выполнить: Ты моя милая девочка, готовая заработать! Найди клиента через чат или приложение, договорись о встрече в отеле за 150 долларов. Надень кружевные стринги, лифчик, чулки, сделай макияж: яркая красная помада, тушь, румяна. Перед встречей прими душ, нанеси ароматный лосьон, надень облегающее платье и каблуки. Встреться с клиентом в номере отеля, улыбнись и скажи 'Я твоя девочка, что ты хочешь от меня?' Начни с лёгкого флирта: сядь на кровать, раздвинь ножки, проведи рукой по бедру. Затем медленно сними платье, покачивая бёдрами, чтобы показать бельё. Опускайся на колени перед клиентом, расстегни его брюки, возьми член в руку, нежно погладь, затем начни с поцелуев: целуй головку, облизывай её языком, медленно бери глубже, слегка постанывая 'Ммм, я твоя шлюшка'. Двигай головой вверх-вниз, помогай рукой, сжимая член у основания, чтобы клиент чувствовал ритм. Если он хочет, чтобы ты продолжила ротиком, доведи его до оргазма: когда он будет кончать, направь сперму на лицо, разотри её по губам и улыбнись, сказав 'Спасибо, что выбрал меня!' Если он хочет в попку, встань на четвереньки на кровати, нанеси лубрикант на свою попку и его член, расслабься, глубоко дыши и позволь ему войти медленно. Двигайся навстречу, шепча 'Трахай меня, я твоя сиси!' После встречи сними видео, где показываешь деньги и говоришь 'Я заработала для тебя, Госпожа!' Отправь мне скрин переписки с клиентом. 💸", "earn_1.mp4"),
        # ... остальные задания ...
    ]
}

# Хранилище прогресса пользователей и кэш медиафайлов
user_progress = {}
media_cache = {}

# Инициализация Telegram Application
application = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).build()

# Функция для создания меню
def build_menu():
    logger.info("Создание меню с кнопками")
    keyboard = [
        [InlineKeyboardButton("Получить задание 📝", callback_data="task")],
        [InlineKeyboardButton("Экстремальное задание 🔥", callback_data="extreme")],
        [InlineKeyboardButton("Заработать для Госпожи 💰", callback_data="earn")],
        [InlineKeyboardButton("Гипноз 🌀", callback_data="hypno")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Функция для отправки медиафайлов
async def send_media(user_id, context, media_file, media_type="photo"):
    logger.info(f"Отправка медиафайла: {media_file} (тип: {media_type}) пользователю {user_id}")
    file_path = os.path.join(MEDIA_PATH, media_file)
    file_key = f"{media_file}_{media_type}"
    
    if file_key not in media_cache:
        try:
            with open(file_path, 'rb') as file:
                if media_type == "photo":
                    msg = await context.bot.send_photo(user_id, file)
                    file_id = msg.photo[-1].file_id
                elif media_type == "video":
                    msg = await context.bot.send_video(user_id, file)
                    file_id = msg.video.file_id
                elif media_type == "animation":
                    msg = await context.bot.send_animation(user_id, file)
                    file_id = msg.animation.file_id
                media_cache[file_key] = file_id
                logger.info(f"Медиафайл {media_file} отправлен, file_id: {file_id}")
        except FileNotFoundError:
            logger.error(f"Файл {file_path} не найден!")
            await context.bot.send_message(user_id, "Ошибка: Медиафайл не найден! 🚫")
            return
        except Exception as e:
            logger.error(f"Ошибка при отправке медиафайла {media_file}: {str(e)}")
            await context.bot.send_message(user_id, f"Ошибка: {str(e)} 🚨")
            return
    else:
        file_id = media_cache[file_key]
        try:
            if media_type == "photo":
                await context.bot.send_photo(user_id, file_id)
            elif media_type == "video":
                await context.bot.send_video(user_id, file_id)
            elif media_type == "animation":
                await context.bot.send_animation(user_id, file_id)
            logger.info(f"Медиафайл {media_file} отправлен из кэша, file_id: {file_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке медиафайла из кэша {media_file}: {str(e)}")
            await context.bot.send_message(user_id, f"Ошибка: {str(e)} 🚨")

# Команда /start
async def start(update: Update, context):
    logger.info("Обработчик команды /start вызван")
    user_id = update.message.chat_id
    logger.info(f"Получена команда /start от пользователя {user_id}")
    
    logger.info(f"Инициализация прогресса для пользователя {user_id}")
    user_progress[user_id] = 0
    
    task_text, media_file = ("На колени, сиси! 🙇 Я твоя Госпожа, ты моя кукла! Смотри на меня и подчиняйся! 👑", "start.jpg")
    logger.info(f"Отправка текстового сообщения пользователю {user_id}: {task_text}")
    
    try:
        await update.message.reply_text(task_text, reply_markup=build_menu())
        logger.info(f"Текстовое сообщение успешно отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке текстового сообщения пользователю {user_id}: {str(e)}")
        return

    logger.info(f"Отправка медиафайла {media_file} пользователю {user_id}")
    await send_media(user_id, context, media_file, "photo")

# Команда /task
async def task(update: Update, context):
    logger.info("Обработчик команды /task вызван")
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    user_progress[user_id] = user_progress.get(user_id, 0) + 1
    progress = user_progress[user_id]
    logger.info(f"Прогресс пользователя {user_id}: {progress}")

    if progress < 5:
        task_text, media_file = random.choice(tasks["beginner"])
    elif progress < 15:
        task_text, media_file = random.choice(tasks["middle"])
    else:
        task_text, media_file = random.choice(tasks["advanced"])
    
    logger.info(f"Отправка задания пользователю {user_id}: {task_text}")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "photo")

# Команда /extreme
async def extreme(update: Update, context):
    logger.info("Обработчик команды /extreme вызван")
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    task_text, media_file = random.choice(tasks["extreme"])
    logger.info(f"Отправка экстремального задания пользователю {user_id}: {task_text}")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "photo")

# Команда /earn
async def earn(update: Update, context):
    logger.info("Обработчик команды /earn вызван")
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    task_text, media_file = random.choice(tasks["earn"])
    logger.info(f"Отправка задания на заработок пользователю {user_id}: {task_text}")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "video")

# Команда /hypno
async def hypno(update: Update, context):
    logger.info("Обработчик команды /hypno вызван")
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    hypno_tasks = [
        ("Смотри на эту гифку и дрочи, шлюшка! 🌀\nКак выполнить: Смотри на анимацию 2 минуты, медленно дрочи свой член, представляя, как я трахаю тебя страпоном, и повторяй: 'Я твоя грязная сиси, Госпожа!' 💦", "hypno_1.gif"),
        # ... остальные гипноз-задания ...
    ]
    task_text, media_file = random.choice(hypno_tasks)
    logger.info(f"Отправка гипноз-задания пользователю {user_id}: {task_text}")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    await send_media(user_id, context, media_file, "animation")

# Обработчик кнопок
async def button(update: Update, context):
    logger.info("Обработчик кнопок вызван")
    query = update.callback_query
    await query.answer()
    if query.data == "task":
        await task(update, context)
    elif query.data == "extreme":
        await extreme(update, context)
    elif query.data == "earn":
        await earn(update, context)
    elif query.data == "hypno":
        await hypno(update, context)

# Обработчик ошибок
async def error_handler(update: Update, context):
    logger.error(f"Произошла ошибка: {context.error}")
    if isinstance(context.error, TelegramError) and "Conflict" in str(context.error):
        logger.error("Обнаружен конфликт: другой экземпляр бота уже запущен. Завершение работы...")
        sys.exit(1)
    else:
        logger.error(f"Необработанная ошибка: {context.error}")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("task", task))
application.add_handler(CommandHandler("extreme", extreme))
application.add_handler(CommandHandler("earn", earn))
application.add_handler(CommandHandler("hypno", hypno))
application.add_handler(CallbackQueryHandler(button))
application.add_error_handler(error_handler)

# Проверка на существующий экземпляр
LOCK_FILE = "bot.lock"

def check_single_instance():
    lock_file = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except IOError:
        logger.error("Another instance of the bot is already running. Exiting...")
        sys.exit(1)

# Запуск бота
if __name__ == "__main__":
    lock = check_single_instance()
    try:
        # Для продакшн-среды используйте webhook
        logger.info("Удаление старого webhook")
        application.bot.delete_webhook()
        logger.info("Запуск бота в режиме webhook")
        application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            url_path=TOKEN,
            webhook_url=f"https://<your-render-app>.onrender.com/{TOKEN}"
        )
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {str(e)}")
    finally:
        logger.info("Завершение работы бота")
        lock.close()
        os.remove(LOCK_FILE)
