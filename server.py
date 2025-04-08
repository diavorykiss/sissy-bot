import logging
import os
import random
from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, CallbackContext

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация бота
TOKEN = os.getenv("BOT_TOKEN", "7622812077:AAGz1Jiaq5IXdfyhqZO3i4aXeHs8EgCOksg")
bot = Bot(token=TOKEN)
# Устанавливаем workers=4 для обработки асинхронных функций
dispatcher = Dispatcher(bot, None, workers=4)

# Настройки медиа (используем file_id вместо локальных файлов)
media = {
    "start": ["start.jpg"],
    "beginner_task": [f"task_{i}.jpg" for i in range(1, 8)],
    "middle_task": [f"task_{i}.jpg" for i in range(8, 16)],
    "advanced_task": [f"task_{i}.jpg" for i in range(1, 8)],
    "extreme": [f"extreme_{i}.jpg" for i in range(1, 9)],
    "earn": [f"earn_{i}.mp4" for i in range(1, 6)],
    "hypno": [f"hypno_{i}.gif" for i in range(1, 29)]
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
        ("Порадуй себя орально для Госпожи! 🍆\nКак выполнить: Надень чулки и лифчик, сядь на пол, наклонись и попробуй достать ртом до своего члена. Ласкай головку язычком, облизывай её, как леденец, и медленно бери глубже, пока не почувствуешь, как он касается горла. Сними видео своих попыток, стоня 'Я твоя послушная куколка, Госпожа, делаю это для тебя!' Покажи, как твой язычок скользит по головке, и не забудь про слюни! 🎥", "extreme_1.jpg"),
        ("Кончи себе в ротик для Госпожи! 💦\nКак выполнить: Накрась губы яркой помадой, ляг на спину, задрав ножки кверху, чтобы член оказался над твоим лицом. Медленно дрочи, лаская головку пальцами, пока не почувствуешь оргазм. Направь струю себе в ротик, проглоти всё до последней капли, сними видео, где ты показываешь сперму на язычке, и скажи 'Я твоя сладкая девочка, Госпожа, всё проглотила для тебя!' 😋", "extreme_2.jpg"),
        ("Ублажай меня язычком, моя игрушка! 👅\nКак выполнить: Надень ошейник и чулки, встань на колени, представь, что я сижу перед тобой с раздвинутыми ножками. Высунь язычок, делай длинные, влажные движения, будто лижешь мою киску, затем переходи к попке, нежно обводя её кончиком языка. Сними видео, где ты стонешь 'Я обожаю лизать тебя, Госпожа, позволь мне служить!' Покажи, как твой язычок двигается, и добавь побольше слюней! 💦", "extreme_3.jpg"),
        ("Кончи на личико для Госпожи! 😈\nКак выполнить: Сделай макияж с красной помадой и smoky eyes, надень кружевное бельё. Встань перед зеркалом, дрочи медленно, лаская головку и сжимая яички, пока не почувствуешь оргазм. Направь струю на своё лицо, чтобы сперма попала на щёчки, губы и подбородок, затем разотри её пальчиками по коже. Сними фото с подписью 'Я твоя похотливая куколка, Госпожа, вся в сперме для тебя!' Покажи, как сперма блестит на твоём лице! 📸", "extreme_4.jpg"),
        ("Соси игрушку на каблуках для Госпожи! 🍭\nКак выполнить: Надень туфли на высоком каблуке, чулки и бельё, возьми дилдо. Встань на колени, облизывай головку дилдо, как конфетку, затем бери его глубже, пока он не упрётся в горло, делай влажные, чавкающие звуки. Сними видео, где ты берёшь его глубоко, стоня 'Я твоя оральная игрушка, Госпожа, трахни мой ротик!' Покажи, как слюни стекают по подбородку, и не забудь улыбнуться в камеру! 🎤", "extreme_5.jpg"),
        ("Играй со спермой для Госпожи! 💧\nКак выполнить: Надень лифчик и трусики, ляг на кровать, дрочи медленно, представляя, что я смотрю на тебя. Когда кончишь, собери сперму пальчиками, разотри её по губам, щёчкам и груди, будто это крем. Сними селфи с подписью 'Я твоя нежная девочка, Госпожа, вся в сперме для тебя!' Покажи, как сперма блестит на твоей коже, и добавь улыбку! 😘", "extreme_6.jpg"),
        ("Трахай попку игрушкой для Госпожи! 🍑\nКак выполнить: Надень платье и чулки, смажь анальную игрушку лубрикантом, вставь её медленно, чувствуя, как она растягивает твою дырочку. Двигай игрушкой взад-вперёд, постепенно ускоряясь, и представляй, что это я вхожу в тебя. Сними видео сзади, стоня 'Госпожа, я твоя анальная куколка, трахни меня глубже!' Покажи, как игрушка входит и выходит, и добавь крупный план дырочки! 🎥", "extreme_7.jpg"),
        ("Глотай сперму с игрушки для Госпожи! 🍆\nКак выполнить: Накрась губы, надень бельё, дрочи, пока не кончишь на дилдо. Затем возьми дилдо в рот, облизывай сперму с головки, бери глубже, чтобы всё проглотить. Сними видео, где ты лижешь сперму, стоня 'Я твоя послушная игрушка, Госпожа, глотаю всё для тебя!' Покажи, как ты облизываешь дилдо, и улыбнись в камеру! 😈", "extreme_8.jpg")
    ],
    "earn": [
        ("Соблазни клиента за деньги для Госпожи! 💰\nКак выполнить: Надень кружевное бельё, чулки, сделай макияж с яркой помадой, найди клиента за 50 долларов. Сними видео, где ты медленно раздеваешься, показываешь бельё, ласкаешь себя пальчиками между ножек и стонешь 'Я твоя похотливая куколка, Госпожа, зарабатываю для тебя!' Пришли скрин переписки с клиентом, где видна договорённость! 📱", "earn_1.mp4"),
        ("Ублажай клиента ротиком за деньги для Госпожи! 🍆\nКак выполнить: Надень каблуки и платье, найди клиента за 100 долларов. Встань на колени, возьми его член в рот, начни с нежных поцелуев головки, затем облизывай её язычком, как леденец, и бери глубже, пока он не упрётся в горло. Делай влажные, чавкающие звуки, смотри ему в глаза и стон 'Я твоя оральная игрушка, Госпожа!' Пусть он кончит тебе на лицо, разотри сперму по щёчкам. Сними фото с деньгами и подписью 'Я зарабатываю для Госпожи!' Покажи сперму на лице и деньги! 📸", "earn_2.mp4"),
        ("Отдайся клиенту за деньги для Госпожи! 💵\nКак выполнить: Надень чулки и бельё, найди клиента за 200 долларов. Начни с минета: облизывай головку, бери член глубоко, ласкай яички язычком, пока он не станет твёрдым. Затем встань на четвереньки, пусть он войдёт в твою попку (используй презерватив и лубрикант), двигайся навстречу, стоня 'Я твоя послушная девочка, Госпожа!' Если презерватив порвался, собери сперму пальчиками, разотри по попке и скажи 'Я вся мокрая для тебя, Госпожа!' Сними видео с деньгами, показывая, как ты двигаешься, и добавь крупный план попки! 🎥", "earn_3.mp4"),
        ("Обслужи клиента полностью за деньги для Госпожи! 💸\nКак выполнить: Надень платье и каблуки, найди клиента за 300 долларов. Начни с минета: целуй головку, облизывай ствол, бери глубоко, пока слюни не потекут по подбородку. Затем ложись на спину, раздвинь ножки, пусть он войдёт в тебя (с презервативом), двигай бёдрами, чтобы он входил глубже, стоня 'Я твоя похотливая куколка, Госпожа!' Если презерватив порвался, пусть кончит тебе в ротик, проглоти всё и покажи пустой рот. Сними видео с деньгами, рассказывая, как ты ублажала клиента, и покажи сперму на губах! 🎤", "earn_4.mp4"),
        ("Ублажай двоих клиентов за деньги для Госпожи! 👬\nКак выполнить: Надень бельё и каблуки, найди двух клиентов за 500 долларов. Начни с минета для одного: облизывай головку, бери глубоко, пока второй ласкает твою попку пальцами. Затем встань на четвереньки, пусть один трахает твою попку (с презервативом), а ты сосёшь второму, двигаясь в ритме. Если презерватив порвался, пусть кончат тебе на попку, разотри сперму по ягодицам. Сними видео, где ты стонешь 'Я твоя послушная игрушка, Госпожа, ублажаю для тебя!' Покажи деньги и сперму на теле с подписью 'Я зарабатываю для Госпожи!' 💰", "earn_5.mp4")
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

# Функция для отправки медиа (используем file_id)
async def send_media(user_id, context, media_file, media_type="photo"):
    file_key = f"{media_file}_{media_type}"
    
    # Используем заранее сохранённые file_id
    file_ids = {
        "start.jpg_photo": os.getenv("START_JPG_FILE_ID", ""),
        "task_1.jpg_photo": os.getenv("TASK_1_JPG_FILE_ID", ""),
        "task_2.jpg_photo": os.getenv("TASK_2_JPG_FILE_ID", ""),
        "task_3.jpg_photo": os.getenv("TASK_3_JPG_FILE_ID", ""),
        "task_4.jpg_photo": os.getenv("TASK_4_JPG_FILE_ID", ""),
        "task_5.jpg_photo": os.getenv("TASK_5_JPG_FILE_ID", ""),
        "task_6.jpg_photo": os.getenv("TASK_6_JPG_FILE_ID", ""),
        "task_7.jpg_photo": os.getenv("TASK_7_JPG_FILE_ID", ""),
        "task_8.jpg_photo": os.getenv("TASK_8_JPG_FILE_ID", ""),
        "task_9.jpg_photo": os.getenv("TASK_9_JPG_FILE_ID", ""),
        "task_10.jpg_photo": os.getenv("TASK_10_JPG_FILE_ID", ""),
        "task_11.jpg_photo": os.getenv("TASK_11_JPG_FILE_ID", ""),
        "task_12.jpg_photo": os.getenv("TASK_12_JPG_FILE_ID", ""),
        "task_13.jpg_photo": os.getenv("TASK_13_JPG_FILE_ID", ""),
        "task_14.jpg_photo": os.getenv("TASK_14_JPG_FILE_ID", ""),
        "task_15.jpg_photo": os.getenv("TASK_15_JPG_FILE_ID", ""),
        "extreme_1.jpg_photo": os.getenv("EXTREME_1_JPG_FILE_ID", ""),
        "extreme_2.jpg_photo": os.getenv("EXTREME_2_JPG_FILE_ID", ""),
        "extreme_3.jpg_photo": os.getenv("EXTREME_3_JPG_FILE_ID", ""),
        "extreme_4.jpg_photo": os.getenv("EXTREME_4_JPG_FILE_ID", ""),
        "extreme_5.jpg_photo": os.getenv("EXTREME_5_JPG_FILE_ID", ""),
        "extreme_6.jpg_photo": os.getenv("EXTREME_6_JPG_FILE_ID", ""),
        "extreme_7.jpg_photo": os.getenv("EXTREME_7_JPG_FILE_ID", ""),
        "extreme_8.jpg_photo": os.getenv("EXTREME_8_JPG_FILE_ID", ""),
        "earn_1.mp4_video": os.getenv("EARN_1_MP4_FILE_ID", ""),
        "earn_2.mp4_video": os.getenv("EARN_2_MP4_FILE_ID", ""),
        "earn_3.mp4_video": os.getenv("EARN_3_MP4_FILE_ID", ""),
        "earn_4.mp4_video": os.getenv("EARN_4_MP4_FILE_ID", ""),
        "earn_5.mp4_video": os.getenv("EARN_5_MP4_FILE_ID", ""),
        "hypno_1.gif_animation": os.getenv("HYPNO_1_GIF_FILE_ID", ""),
        "hypno_2.gif_animation": os.getenv("HYPNO_2_GIF_FILE_ID", ""),
        # Добавьте остальные file_id для hypno_*.gif
    }
    
    if file_key not in file_ids or not file_ids[file_key]:
        await context.bot.send_message(user_id, f"Ошибка: file_id для {media_file} не найден! 🚫")
        return
    
    file_id = file_ids[file_key]
    try:
        if media_type == "photo":
            await context.bot.send_photo(user_id, file_id)
        elif media_type == "video":
            await context.bot.send_video(user_id, file_id)
        elif media_type == "animation":
            await context.bot.send_animation(user_id, file_id)
    except Exception as e:
        await context.bot.send_message(user_id, f"Ошибка при отправке медиа: {str(e)} 🚨")

# Обработчики команд
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    user_progress[user_id] = 0
    task_text, media_file = ("На колени, сиси! 🙇 Я твоя Госпожа, ты моя кукла! Смотри на меня и подчиняйся! 👑", "start.jpg")
    logger.info(f"User {user_id} started the bot")
    await update.message.reply_text(task_text, reply_markup=build_menu())
    await send_media(user_id, context, media_file, "photo")

async def task(update: Update, context: CallbackContext) -> None:
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

async def extreme(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    task_text, media_file = random.choice(tasks["extreme"])
    logger.info(f"User {user_id} requested an extreme task")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "photo")

async def earn(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    task_text, media_file = random.choice(tasks["earn"])
    logger.info(f"User {user_id} requested an earn task")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "video")

async def hypno(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.message.chat_id if update.callback_query else update.message.chat_id
    hypno_tasks = [
        ("Впитай мою власть, куколка! 🌀\nКак выполнить: Смотри на гифку 1 минуту, представляй, как я стою над тобой, а ты целуешь мои туфли, повторяя 'Я твоя послушная игрушка, Госпожа!' Напиши, как ты чувствуешь моё господство! 👑", "hypno_1.gif"),
        ("Погрузись в мои чары, сиси! 👁️\nКак выполнить: Смотри на анимацию 2 минуты, представляй, как мои глаза гипнотизируют тебя, и повторяй 'Я принадлежу Госпоже навсегда!' Опиши, как ты сдаёшься мне! 🧠", "hypno_2.gif"),
        # Добавьте остальные задания для hypno
    ]
    task_text, media_file = random.choice(hypno_tasks)
    logger.info(f"User {user_id} requested a hypno task")
    if update.callback_query:
        await update.callback_query.message.reply_text(task_text, reply_markup=build_menu())
    else:
        await update.message.reply_text(task_text, reply_markup=build_menu())
    
    await send_media(user_id, context, media_file, "animation")

async def button(update: Update, context: CallbackContext) -> None:
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

# Добавляем обработчики в диспетчер
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("task", task))
dispatcher.add_handler(CommandHandler("extreme", extreme))
dispatcher.add_handler(CommandHandler("earn", earn))
dispatcher.add_handler(CommandHandler("hypno", hypno))
dispatcher.add_handler(CallbackQueryHandler(button))

# Маршрут для обработки вебхуков
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Маршрут для установки вебхука
@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")
    return f"Webhook set to {webhook_url}", 200

# Маршрут для проверки состояния (health check)
@app.route("/", methods=["GET"])
def health_check():
    logger.info("Received health check request")
    return "Bot is running", 200

# Запуск приложения
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
# В конец файла server.py
if __name__ == "__main__":
    # Для локального тестирования используем встроенный сервер Flask
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
else:
    # Для продакшена (gunicorn) ничего не делаем
    pass
