import logging
import os
import random
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
import asyncio

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Настройки бота
TOKEN = "7622812077:AAGz1Jiaq5IXdfyhqZO3i4aXeHs8EgCOksg"
MEDIA_PATH = "media"
media = {
    "start": ["start.jpg"],
    "beginner_task": [f"task_{i}.jpg" for i in range(1, 8)],  # task_1.jpg - task_7.jpg
    "middle_task": [f"task_{i}.jpg" for i in range(8, 16)],   # task_8.jpg - task_15.jpg
    "advanced_task": [f"task_{i}.jpg" for i in range(1, 8)],  # Повторно task_1.jpg - task_7.jpg
    "extreme": [f"extreme_{i}.jpg" for i in range(1, 9)],     # extreme_1.jpg - extreme_8.jpg
    "earn": [f"earn_{i}.mp4" for i in range(1, 6)],           # earn_1.mp4 - earn_5.mp4
    "hypno": [f"hypno_{i}.gif" for i in range(1, 29)]         # hypno_1.gif - hypno_28.gif
}
tasks = {
    "beginner": [
        ("Стань моей гладкой сучкой! 🪒\nКак выполнить: Возьми бритву, нанеси пену с запахом клубники и сбрей все волосы с ног, чтобы они блестели, как у шлюшки. Надень прозрачные кружевные чулки, раздвинь ножки перед зеркалом, сделай фото, где видны твои гладкие бёдра и трусики, и отправь Госпоже с подписью 'Я твоя гладкая девочка, готовая служить!' 📸", "task_1.jpg"),
        ("Накрасься как грязная шлюха! 💄\nКак выполнить: Нанеси ярко-алую помаду, сделай smoky eyes с чёрными тенями, добавь накладные ресницы и блеск на щёчки. Надень красные стринги, встань на колени, сделай селфи с язычком наружу и подписью 'Я твоя похотливая сиси, Госпожа, трахни мой ротик!' 💋", "task_2.jpg"),
        ("Сбрей лобок и стань моей игрушкой! ✂️\nКак выполнить: Полностью сбрей волосы на лобке, смажь кожу маслом, чтобы она блестела, надень розовые трусики с вырезом. Сними видео, где раздвигаешь ножки, показываешь гладкую киску и шепчешь 'Моя дырочка готова для тебя, Госпожа!' 🎥", "task_3.jpg"),
        ("Танцуй как похотливая кукла! 👙\nКак выполнить: Надень прозрачные стринги и лифчик, включи музыку, сними видео, где ты крутишь попкой, шлёпаешь себя по ягодицам и стонешь 'Я твоя грязная шлюшка, Госпожа, трахни меня!' Покажи, как твоя попка трясётся! 🍑", "task_4.jpg"),
        ("Поиграй с сосочками как сиси-шлюха! 🍒\nКак выполнить: Надень кружевной лифчик, смочи пальчики слюной, тереби свои соски до твёрдости, сними видео, где ты стонешь 'Мои сисечки хотят твоего язычка, Госпожа!' Покажи крупным планом свои соски и лифчик! 🎥", "task_5.jpg"),
        ("Накажи себя как грязная сучка! 👋\nКак выполнить: Надень чёрные стринги, шлёпни себя по попке 20 раз, чтобы она покраснела, сними видео со звуком шлепков и кричи 'Я плохая шлюха, накажи меня сильнее, Госпожа!' Покажи красную попку крупным планом! 🍑", "task_6.jpg"),
        ("Докажи, что ты моя похотливая кукла! 🪞\nКак выполнить: Накрась губы в розовый, надень женское бельё, встань перед зеркалом, медленно дрочи, представляя, что я трахаю тебя страпоном. Сними видео до оргазма, кричи 'Я твоя сиси, Госпожа, кончаю для тебя!' 💦", "task_7.jpg")
    ],
    "middle": [
        ("Сбрей грудь и стань моей сисястой шлюхой! 🪒\nКак выполнить: Сбреи волосы с груди и подмышек, нанеси блестящий лосьон, надень лифчик с силиконовыми вставками. Сними фото, где ты сжимаешь свои сисечки и пишешь 'Я твоя сисястая куколка, Госпожа, трахни мои сиськи!' ✨", "task_8.jpg"),
        ("Стань моей оральной сучкой! 👅\nКак выполнить: Надень чулки, встань на колени, представь, что я сижу перед тобой с раздвинутыми ногами. Сними видео, где ты лижешь воздух, представляя мою киску, и стонешь 'Я хочу твою мокрую киску, Госпожа, дай мне её!' 💦", "task_9.jpg"),
        ("Сбрей попку как анальная шлюха! ✂️\nКак выполнить: Сбреи волосы между ягодицами, смажь попку маслом, надень стринги с вырезом. Сними видео, где ты раздвигаешь булочки, показываешь дырочку и кричишь 'Моя попка хочет твой страпон, Госпожа!' 🍑", "task_10.jpg"),
        ("Покажи себя в чулках как шлюшка! 🧦\nКак выполнить: Надень чёрные чулки с подвязками, накрась ногти в красный, сними видео, где ты идёшь на каблуках, виляя бёдрами, и говоришь 'Я твоя шлюшка на каблучках, Госпожа, трахни меня!' Покажи, как твоя попка двигается! 👠", "task_11.jpg"),
        ("Ублажай меня как похотливая девочка! 😛\nКак выполнить: Представь, что я сижу на твоём лице в кружевных трусиках. Сними видео, где ты лижешь воздух, представляя, как я теку, и стонешь 'Я хочу лизать твою киску, Госпожа, пока ты не кончишь!' 💋", "task_12.jpg"),
        ("Играй с попкой как анальная сиси! 🍩\nКак выполнить: Надень женские трусики, смажь пальчик, вставь его в попку, сними видео, где ты двигаешь пальцем и стонешь 'Госпожа, моя попка хочет твой страпон!' Покажи, как твоя дырочка сжимается! 🎤", "task_13.jpg"),
        ("Докажи, что ты моя грязная шлюшка! 🍆\nКак выполнить: Надень лифчик и трусики, встань перед зеркалом, дрочи медленно, глядя на себя, сними видео до оргазма, кричи 'Я кончаю для тебя, Госпожа, трахни меня!' Покажи, как сперма стекает по твоему телу! 💦", "task_14.jpg"),
        ("Стань моей анальной куклой! 🔌\nКак выполнить: Надень чулки, смажь анальную пробку, вставь её, сними видео, где ты крутишь попкой и стонешь 'Моя дырочка принадлежит тебе, Госпожа!' Покажи, как пробка входит и выходит! 🍑", "task_15.jpg")
    ],
    "advanced": [
        ("Сбрей всё и стань моей похотливой принцессой! 🪒\nКак выполнить: Сбреи всё тело — ноги, руки, грудь, попку, лобок. Надень платье, чулки, сделай полный макияж с красной помадой. Сними видео, где ты крутишься, показываешь бельё и кричишь 'Я твоя гладкая шлюшка, Госпожа, трахни меня везде!' ✨", "task_1.jpg"),
        ("Шагай как шлюха на каблуках! 👠\nКак выполнить: Надень туфли на высоком каблуке, чулки и мини-юбку, сними видео, где ты идёшь, виляя попкой, поднимаешь юбку, показываешь стринги и кричишь 'Я твоя сиси на каблучках, Госпожа, трахни мою попку!' 🍑", "task_2.jpg"),
        ("Стань моей куклой в платье! 👗\nКак выполнить: Надень платье, лифчик с наполнителем, сделай макияж с длинными ресницами. Сними видео, где ты крутишься, показываешь попку под платьем и стонешь 'Я сиси Госпожи, готовая лизать твою киску!' 🎥", "task_3.jpg"),
        ("Готовь попку как анальная шлюшка! 🍩\nКак выполнить: Надень стринги, смажь игрушку, вставь её в попку, сними видео, где ты двигаешь бёдрами, стонешь 'Госпожа, трахни свою куклу глубже!' Покажи, как игрушка растягивает твою дырочку! 📸", "task_4.jpg"),
        ("Кончи как шлюшка в белье! 👙\nКак выполнить: Надень кружевные трусики и лифчик, дрочи, кончи на бельё, разотри сперму по ткани, сними фото с подписью 'Я грязная девочка для тебя, Госпожа, хочу твой страпон!' Покажи крупным планом мокрое бельё! 💦", "task_5.jpg"),
        ("Соси как моя сиси! 🍌\nКак выполнить: Надень чулки, возьми дилдо или банан, соси его с чавкающими звуками, сними видео, где ты берёшь глубоко в рот и стонешь 'Я твоя оральная шлюшка, Госпожа, трахни мой рот!' Покажи слюни на губах! 🎤", "task_6.jpg"),
        ("Трахай себя как анальная кукла! ✌️\nКак выполнить: Надень женское бельё, вставь два пальца в попку, двигай ими, сними видео с громкими стонами 'Госпожа, я твоя анальная девочка, трахни меня глубже!' Покажи, как твоя дырочка растягивается! 🔥", "task_7.jpg")
    ],
    "extreme": [
        ("Соси себя как грязная шлюха! 🍆\nКак выполнить: Надень чулки и лифчик, попробуй достать ртом до своего члена, сними видео своих усилий, где ты стонешь 'Я твоя грязная сиси, Госпожа, хочу твой член!' Покажи, как ты пытаешься заглотить! 🎥", "extreme_1.jpg"),
        ("Кончи в рот как моя похотливая девочка! 💦\nКак выполнить: Накрась губы, дрочи, кончи себе в рот, проглоти, сними видео, где ты показываешь сперму на языке и кричишь 'Я глотаю для тебя, Госпожа!' Покажи, как ты глотаешь! 😋", "extreme_2.jpg"),
        ("Служи мне как анальная рабыня! 👅\nКак выполнить: Надень ошейник и чулки, представь, что я сижу на твоём лице. Сними видео, где ты лижешь воздух, представляя мою киску, и стонешь 'Я хочу лизать твою попку, Госпожа, накажи меня!' 💦", "extreme_3.jpg"),
        ("Кончи на лицо как грязная шлюшка! 😈\nКак выполнить: Сделай макияж с красной помадой, дрочи, кончи себе на лицо, разотри сперму по губам и щекам, сними фото с подписью 'Я твоя грязная кукла, Госпожа, хочу твой страпон в рот!' Покажи сперму на лице! 📸", "extreme_4.jpg"),
        ("Соси как моя сиси на каблуках! 🍭\nКак выполнить: Надень туфли и бельё, соси дилдо глубоко с чавканьем, сними видео, где ты берёшь его в горло и кричишь 'Я твоя шлюха, Госпожа, трахни мой ротик!' Покажи слюни и глубокий заглот! 🎤", "extreme_5.jpg"),
        ("Играй со спермой как похотливая девочка! 💧\nКак выполнить: Надень лифчик, дрочи, собери сперму после оргазма, разотри по губам и груди, сними селфи с подписью 'Я твоя грязная сиси, Госпожа, хочу лизать твою киску!' Покажи сперму на теле! 😘", "extreme_6.jpg"),
        ("Трахай попку как моя анальная кукла! 🍑\nКак выполнить: Надень платье, вставь игрушку в попку, двигай ею, сними видео сзади, крича 'Госпожа, я твоя анальная шлюшка, трахни меня глубже!' Покажи, как игрушка растягивает твою дырочку! 🎥", "extreme_7.jpg"),
        ("Глотай как моя грязная рабыня! 🍆\nКак выполнить: Накрасься, дрочи, кончи на дилдо, оближи его и проглоти, сними видео с подписью 'Я твоя послушная девочка, Госпожа, глотаю для тебя!' Покажи, как ты лижешь сперму! 😈", "extreme_8.jpg")
    ],
    "earn": [
        ("Стань шлюшкой за деньги! 💰\nКак выполнить: Надень бельё, чулки, сделай макияж с красной помадой, найди клиента за 5000 рублей. Сними видео, где ты виляешь попкой, показываешь бельё и стонешь 'Я твоя шлюшка, Госпожа, зарабатываю для тебя!' Пришли скрин переписки с клиентом! 📱", "earn_1.mp4"),
        ("Докажи, что ты моя проститутка! 💵\nКак выполнить: Надень каблуки и платье, делай минет (лижи головку, бери глубоко, стони как шлюшка), подставляй попку, разотри сперму по лицу. Сними видео с клиентом, где ты кричишь 'Я твоя шлюха, Госпожа!' Покажи деньги в кадре! 🎥", "earn_2.mp4"),
        ("Заработай ротиком как сиси! 🍆\nКак выполнить: Накрась губы, соси медленно, играй язычком, пусть клиент кончит тебе на лицо, разотри сперму. Сними фото с деньгами и подписью 'Я твоя оральная шлюшка, Госпожа!' Покажи сперму на лице и деньги! 📸", "earn_3.mp4"),
        ("Покажи, как служишь за бабки! 💸\nКак выполнить: Надень чулки, после встречи (минет и секс) сними видео с деньгами, расскажи, как ты сосала, подставляла попку и играла со спермой, кричи 'Я твоя шлюха, Госпожа!' Покажи деньги и сперму на теле! 🎤", "earn_4.mp4"),
        ("Обслужи двоих как моя грязная девочка! 👬\nКак выполнить: Надень бельё и каблуки, соси одному, пока второй трахает твою попку. Сними видео, где ты стонешь 'Я твоя шлюха, Госпожа, трахайте меня!' Покажи деньги и сперму на теле с подписью 'Я зарабатываю для Госпожи!' 💰", "earn_5.mp4")
    ]
}
user_progress = {}
media_cache = {}

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
        except FileNotFoundError:
            await context.bot.send_message(user_id, "Ошибка: Медиафайл не найден! 🚫")
            return
        except Exception as e:
            await context.bot.send_message(user_id, f"Ошибка: {str(e)} 🚨")
            return
    else:
        file_id = media_cache[file_key]
        if media_type == "photo":
            await context.bot.send_photo(user_id, file_id)
        elif media_type == "video":
            await context.bot.send_video(user_id, file_id)
        elif media_type == "animation":
            await context.bot.send_animation(user_id, file_id)

async def start(update, context):
    user_id = update.message.chat_id
    user_progress[user_id] = 0
    task_text, media_file = ("На колени, сиси! 🙇 Я твоя Госпожа, ты моя кукла! Смотри на меня и подчиняйся! 👑", "start.jpg")
    logger.info(f"User {user_id} started the bot")
    await update.message.reply_text(task_text, reply_markup=build_menu())
    await send_media(user_id, context, media_file, "photo")

async def task(update, context):
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    user_progress[user_id] = user_progress.get(user_id, 0) + 1
    progress = user_progress[user_id]

    if progress < 5:
        task_text, media_file = random.choice(tasks["beginner"])
    elif progress < 15:
        task_text, media_file = random.choice(tasks["middle"])
    else:
        task_text, media_file = random.choice(tasks["advanced"])
    
    logger.info(f"User {user_id} requested a task (progress: {progress})")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "photo")

async def extreme(update, context):
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    task_text, media_file = random.choice(tasks["extreme"])
    logger.info(f"User {user_id} requested an extreme task")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "photo")

async def earn(update, context):
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    task_text, media_file = random.choice(tasks["earn"])
    logger.info(f"User {user_id} requested an earn task")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "video")

async def hypno(update, context):
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
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
    logger.info(f"User {user_id} requested a hypno task")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "animation")

async def button(update, context):
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

# HTTP-сервер для Render
async def handle_health_check(request):
    logger.info("Received health check request")
    return web.Response(text="Bot is running")

async def start_http_server():
    app = web.Application()
    app.add_routes([web.get('/', handle_health_check)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))  # Render использует переменную PORT, по умолчанию 10000
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"HTTP server started on port {port}")

# Инициализация и запуск бота
def main():
    # Инициализация бота
    application = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).build()

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("task", task))
    application.add_handler(CommandHandler("extreme", extreme))
    application.add_handler(CommandHandler("earn", earn))
    application.add_handler(CommandHandler("hypno", hypno))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск HTTP-сервера
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_http_server())

    # Запуск бота в режиме polling
    logger.info("Starting bot in polling mode")
    application.run_polling()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
