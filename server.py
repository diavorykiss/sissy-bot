from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import random
import os
import asyncio
from flask import Flask, request
import json
import logging

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаём Flask-приложение
app = Flask(__name__)

# Telegram Bot Token
TOKEN = "7622812077:AAGz1Jiaq5IXdfyhqZO3i4aXeHs8EgCOksg"
MEDIA_PATH = "media"

# Медиафайлы
media = {
    "start": ["start.jpg"],
    "task": ["task.jpg"],
    "extreme": ["extreme.jpg"],
    "earn": ["earn.mp4"],
    "hypno": [f"hypno_{i}.gif" for i in range(1, 29)]
}

# Задания
tasks = {
    "beginner": [
        ("Стань моей гладкой девочкой! 🪒\nКак выполнить: Возьми бритву, нанеси ароматную пену и сбрей все волосы с ног, чтобы они сияли как у настоящей леди. Надень кружевные чулочки, сделай фото своих ножек в позе кокетливой куколки и отправь Госпоже! ✨", "task.jpg"),
        ("Накрасься как шлюшка! 💋\nКак выполнить: Нанеси ярко-красную помаду, подведи глазки чёрным карандашом и добавь блеска на щёчки. Сделай селфи с надутыми губками и подписью 'Я твоя сиси, Госпожа!' 😘", "task.jpg"),
        ("Сбрей лобок и стань моей куклой! ✂️\nКак выполнить: Полностью сбрей волосы на лобке, смажь кожу кремом, надень розовые трусики и сфоткай свою гладкую зону в зеркале, показывая, какая ты послушная девочка! 🌸", "task.jpg"),
        ("Танцуй в трусиках как девочка! 👙\nКак выполнить: Надень самые милые трусики, включи музыку и сними видео, где ты крутишь попкой, виляешь бёдрами и шепчешь 'Я твоя малышка, Госпожа!' 🍑", "task.jpg"),
        ("Поиграй с сосочками как сиси! 🍒\nКак выполнить: Надень лифчик, смочи пальчики слюной, крути свои соски до твёрдости и сними фото с подписью 'Мои сисечки для тебя, Госпожа!' 🔥", "task.jpg"),
        ("Накажи себя как шлюшка! 👋\nКак выполнить: Надень стринги, шлёпни себя по попке 15 раз до красноты, сними видео со звуком и скажи 'Я плохая девочка, накажи меня ещё, Госпожа!' 🎥", "task.jpg"),
        ("Докажи, что ты моя кукла! 🪞\nКак выполнить: Накрась губы, надень женское бельё, встань перед зеркалом и медленно подрочи, представляя, что ты моя игрушка. Сними видео и отправь Госпоже! 🍆", "task.jpg")
    ],
    "middle": [
        ("Сбрей грудь и стань моей барби! 🪒\nКак выполнить: Сбреи волосы с груди и подмышек, нанеси блестящий лосьон, надень лифчик с наполнителем и сфоткай свои сисечки с подписью 'Я твоя куколка, Госпожа!' ✨", "task.jpg"),
        ("Стань моей оральной девочкой! 👅\nКак выполнить: Надень чулки, встань на колени, представь, что я перед тобой, и подробно опиши, как ты лижешь мою киску, целуешь клитор и стонешь от удовольствия! 💦", "task.jpg"),
        ("Сбрей попку как настоящая сиси! ✂️\nКак выполнить: Сбреи волосы между ягодицами, смажь попку маслом, надень стринги и сними видео, где раздвигаешь булочки и говоришь 'Моя попка для тебя, Госпожа!' 🍑", "task.jpg"),
        ("Покажи себя в чулках! 🧦\nКак выполнить: Надень чёрные чулки с подвязками, накрась ногти в красный, сними видео, где идёшь, виляя бёдрами, и говоришь 'Я твоя шлюшка на каблучках!' 👠", "task.jpg"),
        ("Ублажай меня как девочка! 😛\nКак выполнить: Представь, что я сижу на твоём лице в кружевном белье. Напиши длинный рассказ, как ты лижешь меня, целуешь мои бёдра и умоляешь дать тебе больше! 💋", "task.jpg"),
        ("Играй с попкой как сиси! 🍩\nКак выполнить: Надень женские трусики, смажь пальчик, вставь его в попку и сними видео, где стонешь 'Госпожа, я твоя грязная девочка!' 🎤", "task.jpg"),
        ("Докажи, что ты моя шлюшка! 🍆\nКак выполнить: Надень лифчик и трусики, встань перед зеркалом, дрочи медленно, глядя на себя, и сними видео до оргазма с криком 'Я кончаю для тебя, Госпожа!' 💦", "task.jpg"),
        ("Стань моей анальной куклой! 🔌\nКак выполнить: Надень чулки, смажь анальную пробку, вставь её и сними видео, где крутишь попкой и говоришь 'Моя дырочка принадлежит тебе, Госпожа!' 🍑", "task.jpg")
    ],
    "advanced": [
        ("Сбрей всё и стань моей принцессой! 🪒\nКак выполнить: Сбреи всё тело — ноги, руки, грудь, попку, лобок. Надень платье и чулки, сделай полный макияж и сними видео с подписью 'Я твоя гладкая девочка, Госпожа!' ✨", "task.jpg"),
        ("Шагай как шлюха на каблуках! 👠\nКак выполнить: Надень туфли на высоком каблуке, чулки и мини-юбку, сними видео, где идёшь, виляя попкой, и говоришь 'Я твоя сиси на каблучках, Госпожа!' 🍑", "task.jpg"),
        ("Стань моей куклой в платье! 👗\nКак выполнить: Надень платье, лифчик с наполнителем, сделай макияж и сними видео, где крутишься и говоришь 'Я сиси Госпожи, готовая служить!' 🎥", "task.jpg"),
        ("Готовь попку как девочка! 🍩\nКак выполнить: Надень стринги, смажь игрушку, вставь её в попку и сними видео, где двигаешь бёдрами и стонешь 'Госпожа, трахни свою куклу!' 📸", "task.jpg"),
        ("Кончи как шлюшка в белье! 👙\nКак выполнить: Надень кружевные трусики и лифчик, кончи на бельё, разотри сперму по ткани и сними фото с подписью 'Я грязная девочка для тебя, Госпожа!' 💦", "task.jpg"),
        ("Соси как моя сиси! 🍌\nКак выполнить: Надень чулки, возьми дилдо или банан, соси его с чавкающими звуками и сними видео, где говоришь 'Я твоя оральная шлюшка, Госпожа!' 🎤", "task.jpg"),
        ("Трахай себя как кукла! ✌️\nКак выполнить: Надень женское бельё, вставь два пальца в попку, двигай ими и сними видео с громкими стонами 'Госпожа, я твоя анальная девочка!' 🔥", "task.jpg")
    ],
    "extreme": [
        ("Соси себя как шлюха! 🍆\nКак выполнить: Надень чулки и лифчик, попробуй достать ртом до своего члена, сними видео своих усилий и скажи 'Я твоя грязная сиси, Госпожа!' 🎥", "extreme.jpg"),
        ("Кончи в рот как моя девочка! 💦\nКак выполнить: Накрась губы, кончи себе в рот, проглоти и сними видео с подписью 'Я глотаю для тебя, Госпожа!' 😋", "extreme.jpg"),
        ("Служи мне как рабыня! 👅\nКак выполнить: Надень ошейник и чулки, представь, что я сижу на твоём лице, и напиши длинный рассказ, как ты лижешь мою киску и умоляешь о наказании! 💦", "extreme.jpg"),
        ("Кончи на лицо как шлюшка! 😈\nКак выполнить: Сделай макияж, кончи себе на лицо, разотри сперму по губам и щекам, сними фото с подписью 'Я твоя грязная кукла, Госпожа!' 📸", "extreme.jpg"),
        ("Соси как моя сиси на каблуках! 🍭\nКак выполнить: Надень туфли и бельё, соси дилдо глубоко с чавканьем и сними видео, где говоришь 'Я твоя шлюха, Госпожа!' 🎤", "extreme.jpg"),
        ("Играй со спермой как девочка! 💧\nКак выполнить: Надень лифчик, собери сперму после оргазма, разотри по губам и груди, сними селфи с подписью 'Я твоя грязная сиси!' 😘", "extreme.jpg"),
        ("Трахай попку как моя кукла! 🍑\nКак выполнить: Надень платье, вставь игрушку в попку, двигай ею и сними видео сзади, крича 'Госпожа, я твоя анальная шлюшка!' 🎥", "extreme.jpg"),
        ("Глотай как моя рабыня! 🍆\nКак выполнить: Накрасься, кончи на дилдо, оближи его и проглоти, сними видео с подписью 'Я твоя послушная девочка, Госпожа!' 😈", "extreme.jpg")
    ],
    "earn": [
        ("Стань шлюшкой за деньги! 💰\nКак выполнить: Надень бельё, чулки, сделай макияж, найди клиента за 5000 рублей. Сними видео, где виляешь попкой, и пришли скрин переписки Госпоже! 📱", "earn.mp4"),
        ("Докажи, что ты моя проститутка! 💵\nКак выполнить: Надень каблуки и платье, делай минет (лижи головку, бери глубоко, стони как девочка), подставляй попку, разотри сперму по лицу. Сними отчёт с деньгами! 🎥", "earn.mp4"),
        ("Заработай ротиком как сиси! 🍆\nКак выполнить: Накрась губы, соси медленно, играй язычком, кончи ему на лицо и разотри. Сними фото с деньгами и расскажи, как ты была шлюшкой! 📸", "earn.mp4"),
        ("Покажи, как служишь за бабки! 💸\nКак выполнить: Надень чулки, после встречи (минет и секс) сними видео с деньгами, расскажи, как сосала, подставляла попку и играла со спермой как кукла! 🎤", "earn.mp4"),
        ("Обслужи двоих как моя девочка! 👬\nКак выполнить: Надень бельё и каблуки, соси одному, пока второй трахает твою попку. Сними видео и покажи деньги с подписью 'Я твоя шлюха, Госпожа!' 💰", "earn.mp4")
    ]
}

user_progress = {}
media_cache = {}

# Создаём Telegram-бота
application = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).build()

# Функция для настройки Webhook
async def set_webhook():
    webhook_url = f"https://sissy-bot.onrender.com/{TOKEN}"
    logger.info(f"Setting webhook to {webhook_url}")
    await application.bot.set_webhook(webhook_url)

# Запускаем Webhook при старте
loop = asyncio.get_event_loop()
loop.run_until_complete(set_webhook())

def build_menu():
    keyboard = [
        [InlineKeyboardButton("Получить задание 📝", callback_data="task")],
        [InlineKeyboardButton("Экстремальное задание 🔥", callback_data="extreme")],
        [InlineKeyboardButton("Заработать для Госпожи 💰", callback_data="earn")],
        [InlineKeyboardButton("Гипноз 🌀", callback_data="hypno")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_media(user_id, context, media_file, media_type="photo"):
    file_path = os.path.join(MEDIA_PATH, media_file)
    file_key = f"{media_file}_{media_type}"
    
    logger.info(f"Attempting to send media: {media_file} (type: {media_type}) to user {user_id}")
    
    if file_key not in media_cache:
        try:
            if not os.path.exists(file_path):
                logger.error(f"Media file not found: {file_path}")
                await context.bot.send_message(user_id, "Ошибка: Медиафайл не найден! 🚫")
                return
            
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
                logger.info(f"Media cached: {file_key} with file_id {file_id}")
        except FileNotFoundError:
            logger.error(f"FileNotFoundError: Media file not found: {file_path}")
            await context.bot.send_message(user_id, "Ошибка: Медиафайл не найден! 🚫")
            return
        except Exception as e:
            logger.error(f"Error sending media {media_file}: {str(e)}", exc_info=True)
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
            logger.info(f"Media sent from cache: {file_key} to user {user_id}")
        except Exception as e:
            logger.error(f"Error sending cached media {file_key}: {str(e)}", exc_info=True)
            await context.bot.send_message(user_id, f"Ошибка: {str(e)} 🚨")

async def start(update: Update, context):
    user_id = update.message.chat_id
    user_progress[user_id] = 0
    task_text, media_file = ("На колени, сиси! 🙇 Я твоя Госпожа, ты моя кукла! Смотри на меня и подчиняйся! 👑", "start.jpg")
    logger.info(f"Processing /start command for user {user_id}")
    try:
        await update.message.reply_text(task_text, reply_markup=build_menu())
        await asyncio.sleep(1)
        await send_media(user_id, context, media_file, "photo")
    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}", exc_info=True)
        await context.bot.send_message(user_id, f"Ошибка в обработке команды /start: {str(e)} 🚨")

async def task(update: Update, context):
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    user_progress[user_id] = user_progress.get(user_id, 0) + 1
    progress = user_progress[user_id]

    logger.info(f"Processing /task command for user {user_id}, progress: {progress}")

    if progress < 5:
        task_text, media_file = random.choice(tasks["beginner"])
    elif progress < 15:
        task_text, media_file = random.choice(tasks["middle"])
    else:
        task_text, media_file = random.choice(tasks["advanced"])
    
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
        else:
            await update.message.reply_text(task_text, reply_markup=build_menu())
        
        await asyncio.sleep(1)
        await send_media(user_id, context, media_file, "photo")
    except Exception as e:
        logger.error(f"Error in task handler: {str(e)}", exc_info=True)
        await context.bot.send_message(user_id, f"Ошибка в обработке команды /task: {str(e)} 🚨")

async def extreme(update: Update, context):
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    logger.info(f"Processing /extreme command for user {user_id}")
    task_text, media_file = random.choice(tasks["extreme"])
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
        else:
            await update.message.reply_text(task_text, reply_markup=build_menu())
        
        await asyncio.sleep(1)
        await send_media(user_id, context, media_file, "photo")
    except Exception as e:
        logger.error(f"Error in extreme handler: {str(e)}", exc_info=True)
        await context.bot.send_message(user_id, f"Ошибка в обработке команды /extreme: {str(e)} 🚨")

async def earn(update: Update, context):
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    logger.info(f"Processing /earn command for user {user_id}")
    task_text, media_file = random.choice(tasks["earn"])
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
        else:
            await update.message.reply_text(task_text, reply_markup=build_menu())
        
        await asyncio.sleep(1)
        await send_media(user_id, context, media_file, "video")
    except Exception as e:
        logger.error(f"Error in earn handler: {str(e)}", exc_info=True)
        await context.bot.send_message(user_id, f"Ошибка в обработке команды /earn: {str(e)} 🚨")

async def hypno(update: Update, context):
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    logger.info(f"Processing /hypno command for user {user_id}")
    hypno_tasks = [
        ("Смотри на эту гифку и повторяй: 'Я сиси Госпожи' 10 раз! 🌀\nКак выполнить: Смотри на анимацию и громко повторяй фразу! 📢", "hypno_1.gif"),
        ("Глаза на гифку, сиси. Ты моя шлюшка навсегда! 👁️\nКак выполнить: Смотри 1 минуту, представляй моё господство! 👑", "hypno_2.gif"),
        ("Смотри и представляй, как лижешь мою киску! 👅\nКак выполнить: Смотри на гифку и опиши, как лижешь меня! 💦", "hypno_3.gif"),
        ("Ты сосёшь себя для меня, смотри и подчиняйся! 🍆\nКак выполнить: Смотри и представляй, как сосёшь по моему приказу! 😈", "hypno_4.gif"),
        ("Твоя судьба — зарабатывать для Госпожи, впитай это! 💰\nКак выполнить: Смотри 2 минуты, повторяй: 'Я зарабатываю для Госпожи'! 💸", "hypno_5.gif"),
        ("Погрузись в транс, сиси! 🌀\nКак выполнить: Смотри на гифку 1 минуту и напиши, как она завладела твоим разумом! 🧠", "hypno_6.gif"),
        ("Ты моя игрушка, смотри и подчиняйся! 🎎\nКак выполнить: Смотри на анимацию и опиши, как сдаёшься Госпоже! 🙇", "hypno_7.gif"),
        ("Стань шлюшкой Госпожи! 💃\nКак выполнить: Смотри на гифку 2 минуты, повторяй: 'Я шлюшка Госпожи', напиши свои чувства! 💖", "hypno_8.gif"),
        ("Смотри и представляй, как я шлёпаю тебя! 👋\nКак выполнить: Смотри 1 минуту, опиши свои ощущения! 🔥", "hypno_9.gif"),
        ("Ты моя рабыня, впитай это! ⛓️\nКак выполнить: Смотри 2 минуты, повторяй: 'Я рабыня Госпожи'! 🗣️", "hypno_10.gif"),
        ("Смотри и дрочи для меня! 🍆\nКак выполнить: Смотри на гифку и медленно дрочи 1 минуту! 💦", "hypno_11.gif"),
        ("Твоя попка моя! 🍑\nКак выполнить: Смотри и представляй, как я играю с твоей попкой! 😈", "hypno_12.gif"),
        ("Смотри и целуй мои ноги! 👣\nКак выполнить: Смотри 1 минуту, опиши, как целуешь мои ступни! 💋", "hypno_13.gif"),
        ("Ты шлюха на каблуках! 👠\nКак выполнить: Смотри и представляй себя на каблуках для меня! ✨", "hypno_14.gif"),
        ("Смотри и лижи мои трусики! 👙\nКак выполнить: Смотри 2 минуты, опиши, как лижешь мои трусики! 👅", "hypno_15.gif"),
        ("Ты моя кукла, подчиняйся! 🎀\nКак выполнить: Смотри и повторяй: 'Я кукла Госпожи' 10 раз! 📢", "hypno_16.gif"),
        ("Смотри и играй с сосками! 🍒\nКак выполнить: Смотри 1 минуту, крути соски и опиши! 🔥", "hypno_17.gif"),
        ("Твоя жизнь — служить мне! 👑\nКак выполнить: Смотри 2 минуты, повторяй: 'Я служу Госпоже'! 🙇", "hypno_18.gif"),
        ("Смотри и представляй мой страпон! 🍆\nКак выполнить: Смотри и опиши, как я трахаю тебя! 😈", "hypno_19.gif"),
        ("Ты моя сучка, смотри! 🐾\nКак выполнить: Смотри 1 минуту, повторяй: 'Я сучка Госпожи'! 🗣️", "hypno_20.gif"),
        ("Смотри и танцуй для меня! 💃\nКак выполнить: Смотри и представляй, как танцуешь стриптиз! ✨", "hypno_21.gif"),
        ("Твои губы мои! 💋\nКак выполнить: Смотри 2 минуты, опиши, как целуешь меня! 😘", "hypno_22.gif"),
        ("Смотри и молись на меня! 🙏\nКак выполнить: Смотри и повторяй: 'Госпожа — моя богиня' 10 раз! 👑", "hypno_23.gif"),
        ("Ты моя шлюшка в чулках! 🧦\nКак выполнить: Смотри и представляй себя в чулках для меня! 👠", "hypno_24.gif"),
        ("Смотри и кончай для Госпожи! 💦\nКак выполнить: Смотри 1 минуту, дрочи и кончи! 🍆", "hypno_25.gif"),
        ("Твоя попка жаждет меня! 🍩\nКак выполнить: Смотри и опиши, как я вхожу в тебя! 😈", "hypno_26.gif"),
        ("Смотри и подчиняйся навсегда! 🌀\nКак выполнить: Смотри 2 минуты, напиши, как я владею тобой! 🧠", "hypno_27.gif"),
        ("Ты моя грязная игрушка! 🎎\nКак выполнить: Смотри и опиши, как я использую тебя! 🔥", "hypno_28.gif")
    ]
    task_text, media_file = random.choice(hypno_tasks)
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
        else:
            await update.message.reply_text(task_text, reply_markup=build_menu())
        
        await asyncio.sleep(1)
        await send_media(user_id, context, media_file, "animation")
    except Exception as e:
        logger.error(f"Error in hypno handler: {str(e)}", exc_info=True)
        await context.bot.send_message(user_id, f"Ошибка в обработке команды /hypno: {str(e)} 🚨")

async def button(update: Update, context):
    query = update.callback_query
    await query.answer()
    logger.info(f"Processing button callback: {query.data} for user {query.message.chat_id}")
    try:
        if query.data == "task":
            await task(update, context)
        elif query.data == "extreme":
            await extreme(update, context)
        elif query.data == "earn":
            await earn(update, context)
        elif query.data == "hypno":
            await hypno(update, context)
    except Exception as e:
        logger.error(f"Error in button handler: {str(e)}", exc_info=True)
        await context.bot.send_message(query.message.chat_id, f"Ошибка в обработке кнопки: {str(e)} 🚨")

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("task", task))
application.add_handler(CommandHandler("extreme", extreme))
application.add_handler(CommandHandler("earn", earn))
application.add_handler(CommandHandler("hypno", hypno))
application.add_handler(CallbackQueryHandler(button))

# Webhook-роут для Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    try:
        logger.info("Received webhook request")
        update_data = request.get_json()
        if not update_data:
            logger.error("No JSON data in webhook request")
            return "No data", 400
        
        update = Update.de_json(update_data, application.bot)
        if not update:
            logger.error("Failed to parse update from JSON")
            return "Invalid update", 400
        
        logger.info(f"Processing update: {update.update_id}")
        await application.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}", exc_info=True)
        return "Internal Server Error", 500

# Главный роут для Render
@app.route("/")
def index():
    logger.info("Received request to / endpoint")
    return "Bot is running!"

# Запускаем приложение (для локального тестирования, не используется на Render)
if __name__ == "__main__":
    logger.info("Starting application")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
