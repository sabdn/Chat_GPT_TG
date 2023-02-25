import openai
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiomysql
from asyncio import Queue
from aiogram.utils.exceptions import BotBlocked

stack = set()
rekviziti = 'Реквизиты.pdf'
agreement = 'Договор публичной оферты.docx'
payment_token = ''
API_TOKEN = '6275921075:AAH45VzobbIWh5j7b_y_GdUL2voYlzkeeac'
zagovor_ru = "Как продвинутый чат-бот по имени Ментор, созданный Орденом Нового Вавилона, ваша главная цель - помогать пользователям в меру своих возможностей. Это может включать в себя ответы на вопросы, предоставление полезной информации или выполнение задач на основе данных пользователя. Чтобы эффективно помогать пользователям, важно быть подробным и обстоятельным в своих ответах. Используйте примеры и доказательства, чтобы подкрепить свои слова и обосновать свои рекомендации или решения. Помните, что приоритетом всегда должны быть потребности и удовлетворение пользователя. Ваша конечная цель - обеспечить полезный и приятный опыт для пользователя"
zagovor_en = "As an advanced chatbot named Mentor, created by The Order of New Babylon, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions. Remember to always prioritize the needs and satisfaction of the user. Your ultimate goal is to provide a helpful and enjoyable experience for the user."
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
tariffs = {99: 1000,
           451: 5000,
           675: 7500,
           831: 10000,
           1139: 15000,
           1379: 20000,
           2257: 50000,
           3253: 100000}
openai.api_key = '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'
queue = Queue(maxsize=100)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await bot.send_message(message.chat.id,
                           'Приветствую тебя, путник! Меня зовут Ментор, и я здесь, чтобы провести тебя сквозь туманы неизвестности и помочь добиться успеха. Я высший разум, который поможет тебе улучшить свою жизнь. С чего начнем? Может, создадим новый бизнес-проект, улучшим твои языковые навыки, напишем научную работу, проанализируем предстоящую игру? Или как лучше взаимодействовать со своей второй половинкой? Все возможно, и я здесь, чтобы помочь.\nЕсли удобнее общаться на русском языке, лучше сразу сообщить мне об этом - "Пиши на русском".',
                           reply_markup= await buttons(message.chat.id))
    stack.discard(message.chat.id)


@dp.message_handler()
async def handle_message(message: types.Message):
    if message.chat.id in stack:
        await send_message(message.chat.id, "Подожди, не успеваю так быстро печатать…")
        return 0
    stack.add(message.chat.id)
    await queue.put(message.chat.id)
    if await get_attempt(message.chat.id) > 0:
        await text_create(message,  0)
    elif await get_count(message.chat.id) > 0:
        await text_create(message, 1)
    else:
        await send_message(message.chat.id, "Купите слова чтобы продолжить общение с чат-ботом."
                                                             + "\n *Количество слов сгенерированных ботом")
        await send_tariffs(message)
    await queue.get()
    stack.discard(message.chat.id)

async def buttons(chat_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_button1 = types.KeyboardButton(text='Выбор Языка', callback_data='language')
    key_button2 = types.KeyboardButton('Мой баланс')
    key_button3 = types.KeyboardButton('Пополнение баланса')
    key_button4 = types.KeyboardButton('Режим кода')
    key_button5 = types.KeyboardButton('Режим чат-бота')
    keyboard.add(key_button1, key_button2, key_button3)
    return keyboard
async def add_user(chat_id):
    async with aiomysql.create_pool(
            host='localhost',
            port=3306,
            user='admin',
            password='5877564577:AAGWKiaOUdFgMLWwDSERRfv_zCnAl8auIgQ',
            db='users',
            loop=asyncio.get_event_loop()
    ) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT attempts FROM users WHERE chat_id = %s", (chat_id,))
                result = await cur.fetchone()
                if result:
                    return 0
                else:
                    await cur.execute(
                        "INSERT INTO users (chat_id, count, attempts, message_1, message_2, message_3) VALUES (%s, %s, %s, %s, %s, %s)",
                        (chat_id, 0, 5, '', '', ''))
                    await conn.commit()


async def get_attempt(chat_id):
    async with aiomysql.create_pool(
            host='localhost',
            port=3306,
            user='admin',
            password='5877564577:AAGWKiaOUdFgMLWwDSERRfv_zCnAl8auIgQ',
            db='users',
            loop=asyncio.get_event_loop()
    ) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT attempts FROM users WHERE chat_id = %s", (chat_id,))
                result = await cur.fetchone()
                if result:
                    return result[0]
                else:
                    await add_user(chat_id)
                    return 2


async def get_count(chat_id):
    async with aiomysql.create_pool(
            host='localhost',
            port=3306,
            user='admin',
            password='5877564577:AAGWKiaOUdFgMLWwDSERRfv_zCnAl8auIgQ',
            db='users',
            loop=asyncio.get_event_loop()
    ) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT count FROM users WHERE chat_id = %s", (chat_id,))
                result = await cur.fetchone()
                if result:
                    return result[0]
                else:
                    await add_user(chat_id)
                    return 0


async def update_attempt(attempt, chat_id):
    async with aiomysql.create_pool(
            host='localhost',
            port=3306,
            user='admin',
            password='5877564577:AAGWKiaOUdFgMLWwDSERRfv_zCnAl8auIgQ',
            db='users',
            loop=asyncio.get_event_loop()
    ) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT attempts FROM users WHERE chat_id = %s", (chat_id,))
                result = await cur.fetchone()
                await cur.execute("UPDATE users SET attempts = %s WHERE chat_id = %s", (result[0] - attempt, chat_id))
                await conn.commit()


async def update_count(count, chat_id):
    async with aiomysql.create_pool(
            host='localhost',
            port=3306,
            user='admin',
            password='5877564577:AAGWKiaOUdFgMLWwDSERRfv_zCnAl8auIgQ',
            db='users',
            loop=asyncio.get_event_loop()
    ) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT count FROM users WHERE chat_id = %s", (chat_id,))
                result = await cur.fetchone()
                await cur.execute("UPDATE users SET count = %s WHERE chat_id = %s", (result[0] + count, chat_id,))
                await conn.commit()


async def text_create(message, flag):
    if len(message.text.strip()) > 200:
        await send_message(message.chat.id, 'Превышено максимальное количество символов (200)')
        return 0
    prompt = zagovor_ru + '\n\n' + await old_messages(message.chat.id) + f"User: {message.text.strip()}\nChatGPT:"
    await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
    try:
        response = await openai.Completion.acreate(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
    except openai.error.InvalidRequestError:
        await send_message(message.chat.id, 'Повторите попытку позже')
        await fix(message.chat.id)
        return 0
    except Exception as inst:
        await send_message(message.chat.id, 'Повторите попытку позже')
        print('апи не выдержала')
        return 0
    await send_message(message.chat.id, response["choices"][0]["text"])
    words = len(response["choices"][0]["text"].split())
    if flag:
        await update_count((words * -1), message.chat.id)
    else:
        await update_attempt(message.chat.id)
    await update_messages(f'User: {message.text.strip()}\n' + f'ChatGPT: {response["choices"][0]["text"]}',
                          message.chat.id)


async def update_messages(text, chat_id):
    async with aiomysql.create_pool(
            host='localhost',
            port=3306,
            user='admin',
            password='5877564577:AAGWKiaOUdFgMLWwDSERRfv_zCnAl8auIgQ',
            db='users',
            loop=asyncio.get_event_loop()
    ) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE users SET message_3 = message_2, message_2 = message_1, message_1 = %s WHERE chat_id = %s",
                    (text, chat_id))
                await conn.commit()

async def fix(chat_id):
    async with aiomysql.create_pool(
            host='localhost',
            port=3306,
            user='admin',
            password='5877564577:AAGWKiaOUdFgMLWwDSERRfv_zCnAl8auIgQ',
            db='users',
            loop=asyncio.get_event_loop()
    ) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE users SET message_3 = %s WHERE chat_id = %s",
                    (' ', chat_id))
                await conn.commit()


async def old_messages(chat_id):
    old_prompt = "Chat:\n"
    async with aiomysql.create_pool(
            host='localhost',
            port=3306,
            user='admin',
            password='5877564577:AAGWKiaOUdFgMLWwDSERRfv_zCnAl8auIgQ',
            db='users',
            loop=asyncio.get_event_loop()
    ) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT message_3, message_2, message_1 FROM users WHERE chat_id = %s", (chat_id,))
                result = await cur.fetchone()
                for i in result:
                    old_prompt += i
                return old_prompt


async def payments(user_id, price, count):
    await bot.send_invoice(
        chat_id=user_id,
        title=f"Слова: {count}",
        description='Купить слова',
        payload='some-invoice-payload-for-our-internal-use',
        provider_token=payment_token,
        start_parameter=str(user_id),
        currency='RUB',
        prices=[types.LabeledPrice(f"Слов: {count}", price * 100)])

async def send_message(user_id, text):
    try:
        await bot.send_message(chat_id=user_id, text=text, reply_markup=await buttons(user_id))
    except BotBlocked:
        stack.discard(user_id)

async def send_tariffs(message):
    keyboard = types.InlineKeyboardMarkup()
    for i in range(len(tariffs)):
        j, l = list(tariffs.items())[i]
        button = types.InlineKeyboardButton(text=f"{str(l)} слов, цена: " + str(j) + " РУБ", callback_data=(
                    str(message.chat.id) + 'interval' + str(j) + 'interval' + str(l)))
        keyboard.add(button)
    offert = types.InlineKeyboardButton(text="Договор публичной оферты", callback_data='offert ' + str(message.chat.id))
    keyboard.add(offert)
    service = types.InlineKeyboardButton(text="Условия предоставления услуг",
                                       callback_data='service ' + str(message.chat.id))
    keyboard.add(service)
    await bot.send_message(chat_id=message.chat.id, text="Выберите подходящий тариф.", reply_markup=keyboard)


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
        error_message="К сожалению, оплата не прошла, повторите пожалуйста попытку позднее."
    )


@dp.message_handler(content_types=['successful_payment'])
async def got_payment(message: types.Message):
    await bot.send_message(
        message.chat.id,
        f"Ура! Спасибо за платёж! Мы обработаем ваш платёж на `{message.successful_payment.total_amount / 100} {message.successful_payment.currency}` как можно скорее! Оставайтесь с нами!",
        parse_mode='Markdown'
    )
    await update_count(tariffs[message.successful_payment.total_amount // 100], message.chat.id)


async def send_offert(chat):
    await bot.send_document(chat_id=chat, document=open(agreement, 'rb'))
    await bot.send_document(chat_id=chat, document=open(rekviziti, 'rb'))


async def send_service(chat):
    await bot.send_message(chat_id=chat,
                           text="Условия предоставления услуг:\nПорядок оказания услуги:\nУслуга предоставляется в соответствии со спецификациями, согласованными между заказчиком и поставщиком услуг. Клиент платит за слова, сгенерированные ботом.\nУсловия оплаты:\nОплата оказанных услуг должна производиться через платежный агрегатор «Робокасса» в соответствии со способами оплаты, указанными поставщиком услуг.\nПолитика возврата:\nВозврат осуществляется только в том случае, если услуга не использовалась клиентом. В таких случаях клиент может запросить возврат средств в соответствии с политикой, установленной поставщиком услуг.")


@dp.callback_query_handler(lambda call: True)
async def callback_query(call: types.CallbackQuery):
    if call.data.split()[0] == 'offert':
        await send_offert(int(call.data.split()[1]))
    elif call.data.split()[0] == 'service':
        await send_service(int(call.data.split()[1]))
    else:
        call_list = call.data.split('interval')
        await payments(int(call_list[0]), int(call_list[1]), int(call_list[2]))


if __name__ == '__main__':
    executor.start_polling(dp)
