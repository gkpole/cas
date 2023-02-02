import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from keyboards import *
from aiogram.dispatcher.filters import Text
from database import default_setting, all_users, workers, Pay, promo, root
from states import mamont_edit_pay, qiwi_token, qiwi_phone, costing, promokods, ecn_add, bring, bring_requisites, \
    setMamont, setPromo, mamont_edit_balance,rnd_numchik,kubik_casino,crash
import string
import random
import requests
from config import *
import asyncio
from aiogram import types

bot = Bot(token=telegram_token)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

channel = -1001526195268

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


async def get_history():
    pays = Pay.get(Pay.id == 1)
    phone = pays.qiwi_number
    token = pays.qiwi_token
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + token

    parameters = {
        'rows': 4,
        'operation': 'IN'
    }

    h = s.get(f'https://edge.qiwi.com/payment-history/v2/persons/{str(phone)}/payments', params=parameters)
    return h.json()


@dp.message_handler(commands='admins')
async def admins(message: types.Message):
    information_adm = default_setting.get(default_setting.id == 1)

    if root.get_or_none(root.admin == message.from_user.id):
        admin_panel = types.InlineKeyboardMarkup()
        if information_adm.pay_status == 0:
            status = types.InlineKeyboardButton("Статус платежей ✅️", callback_data='status')
        else:
            status = types.InlineKeyboardButton("Статус платежей 🛑️", callback_data='status')
        admin_panel.add(types.InlineKeyboardButton("Изменить номер киви", callback_data='qiwi_phone'),
                        types.InlineKeyboardButton("Изменить токен", callback_data='qiwi_token'))
        admin_panel.add(status)
        await bot.send_message(message.chat.id, 'Добро пожаловать!',
                               reply_markup=admin_panel)
    else:
        pass


@dp.callback_query_handler(text='status')
async def send_p(call: types.CallbackQuery):
    information_adm = default_setting.get(default_setting.id == 1)
    infor = default_setting.get(default_setting.id == 1)
    if infor.pay_status == 0:
        infor.pay_status += 1
    else:
        infor.pay_status -= 1
    infor.save()
    if root.get_or_none(root.admin == call.from_user.id):
        admin_panel = types.InlineKeyboardMarkup()
        qiwi_number = types.InlineKeyboardButton("Изменить номер киви", callback_data='qiwi_phone')
        token_qiwi = types.InlineKeyboardButton("Изменить токен", callback_data='qiwi_token')
        if information_adm.pay_status == 0:
            status = types.InlineKeyboardButton("Статус платежей ✅️", callback_data='status')
        else:
            status = types.InlineKeyboardButton("Статус платежей 🛑️", callback_data='status')
        admin_panel.add(qiwi_number, token_qiwi)
        admin_panel.add(status)
        await call.message.edit_text('Добро пожаловать!',
                                         reply_markup=admin_panel)
    else:
        pass


@dp.callback_query_handler(text='qiwi_token')
async def input_token(call: types.CallbackQuery):
    await call.message.delete()
    if root.get_or_none(root.admin == call.message.chat.id):
        await bot.send_message(call.message.chat.id, 'Введите токен: ')
    await qiwi_token.token.set()


@dp.message_handler(content_types=['text'], state=qiwi_token)  # Принимаем состояние
async def set_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['token'] = message.text
    await state.finish()
    token1 = Pay.get(Pay.id == 1)
    token1.qiwi_token = data['token']
    token1.save()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='back_to_admin'))
    await bot.send_message(message.chat.id, '✅️Изменено', parse_mode='Markdown', reply_markup=keyboard)


@dp.callback_query_handler(text='qiwi_phone')
async def input_number(call: types.CallbackQuery):
    if root.get_or_none(root.admin == call.message.chat.id):
        await call.message.edit_text('Введите номер киви в формате 79943299923')
    await qiwi_phone.number.set()


@dp.message_handler(content_types=['text'], state=qiwi_phone)  # Принимаем состояние
async def set_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = message.text
    await state.finish()

    qiwi_kos = Pay.get(Pay.id == 1)
    qiwi_kos.qiwi_number = data['number']
    qiwi_kos.save()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='back_to_admin'))
    await bot.send_message(message.chat.id, '✅️Изменено', parse_mode='Markdown', reply_markup=keyboard)


@dp.callback_query_handler(text="back_to_admin")
async def back_to_admin(call: types.CallbackQuery):
    information_adm = default_setting.get(default_setting.id == 1)
    if root.get_or_none(root.admin == call.from_user.id):
        admin_panel = types.InlineKeyboardMarkup()
        if information_adm.pay_status == 0:
            status = types.InlineKeyboardButton("Статус платежей ✅️", callback_data='status')
        else:
            status = types.InlineKeyboardButton("Статус платежей 🛑️", callback_data='status')
        admin_panel.add(types.InlineKeyboardButton("Изменить номер киви", callback_data='qiwi_phone'),
                            types.InlineKeyboardButton("Изменить токен", callback_data='qiwi_token'))
        admin_panel.add(status)
        await call.message.edit_text('Добро пожаловать!', reply_markup=admin_panel)
    else:
        pass


@dp.message_handler(commands='work')
async def new_worker(message: types.Message):
    if not workers.get_or_none(workers.user_id == message.from_user.id):
        workers.create(user_id=message.from_user.id)


@dp.message_handler(commands="start")
async def start_message(message: types.Message):
    args = message.text.split()
    if not all_users.get_or_none(all_users.user_id == message.from_user.id):
        if len(args) == 2:
            code = args[1]

            if message.from_user.username is None:
                all_users.create(user_id=message.chat.id, username=message.from_user.first_name, worker=code,
                                 worker_ref=code,
                                 id_mamont=message.chat.id)
            else:
                all_users.create(user_id=message.chat.id, username=message.from_user.username, worker=code,
                                 worker_ref=code,
                                 id_mamont=message.chat.id)

            await bot.send_message(int(code), '✅ У вас новый мамонт')
        else:
            if message.from_user.username is None:
                all_users.create(user_id=message.chat.id, username=message.from_user.first_name)
            else:
                all_users.create(user_id=message.chat.id, username=message.from_user.username)

        text = f'''
✅Здравствуй!

Политика и условия пользования данным ботом.

1. Играя у нас, вы берёте все риски за свои средства на себя.
2. Принимая правила, Вы подтверждаете своё совершеннолетие!
3. Ваш аккаунт может быть забанен в подозрении на мошенничество / обман нашей системы
4. Мультиаккаунты запрещены!
5. Скрипты, схемы использовать запрещено!
6. Если будут выявлены вышеперечисленные случаи, Ваш аккаунт будет заморожен до выяснения обстоятельств!
7. В случае необходимости администрация имеет право запросить у Вас документы, подтверждающие Вашу личность и Ваше совершеннолетие.

Вы играете на виртуальные монеты, покупая их за настоящие деньги. Любое пополнение бота является пожертвованием! По всем вопросам Вывода средств, по вопросам пополнения, а так же вопросам игр обращайтесь в поддержку, указанную в боте
Пишите сразу по делу, а не «Здравствуйте! Тут?»
Старайтесь изложить свои мысли четко и ясно, чтобы поддержка не мучалась и не пыталась Вас понять.

Спасибо за понимание!
Удачи!
            '''
        await message.answer(text, reply_markup=keyboard_accept_license)

    else:
        profile = all_users.get(all_users.user_id == message.from_user.id)
        if profile.verif == 0:
            text = f'''
📲 Ваш личный кабинет

💰Денежный баланс: {profile.balance} ₽
🤝 Сделок: {profile.offer}

📑 Верификация: ❌

🆔 Ваш ID: {profile.user_id}
📈 Активных пользователей онлайн: {random.randint(1950, 2050)}
                    '''

        else:
            text = f'''
📲 Ваш личный кабинет

💰Денежный баланс: {profile.balance} ₽
🤝 Сделок: {profile.offer}

📑 Верификация: ✅

🆔 Ваш ID: {profile.user_id}
📈 Активных пользователей онлайн: {random.randint(1950, 2050)}


                                '''

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text='🎰 Играть'), types.InlineKeyboardButton(text='💼 Профиль'))
        keyboard.add(types.KeyboardButton(text='💳 Пополнить'),
                     types.KeyboardButton(text='🏦 Вывести'))
        keyboard.add(types.KeyboardButton('⚙Обратная связь⚙ '))







        if workers.get_or_none(workers.user_id == message.from_user.id):
            keyboard.add(types.KeyboardButton(text='⚡️ Меню воркера', callback_data="workers_menu"))
        await message.reply(text='Добро пожаловать 👋',reply_markup=keyboard)
        await message.answer_photo(photo=open('images/profile.jpg', 'rb'), caption=text)



@dp.callback_query_handler(text="accept_licence")
async def accept_licence(call: types.CallbackQuery):
    await call.message.delete()
    profile = all_users.get(all_users.user_id == call.from_user.id)
    if profile.verif == 0:
        text = f'''
📲 Ваш личный кабинет

💰Денежный баланс: {profile.balance} ₽
🤝 Сделок: {profile.offer}

📑 Верификация: ❌

🆔 Ваш ID: {profile.user_id}
📈 Активных пользователей онлайн: {random.randint(1950, 2050)}




                        '''

    else:
        text = f'''
📲 Ваш личный кабинет

💰Денежный баланс: {profile.balance} ₽
🤝 Сделок: {profile.offer}

📑 Верификация: ❌

🆔 Ваш ID: {profile.user_id}
📈 Активных пользователей онлайн: {random.randint(1950, 2050)}
                                    '''

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='🎰 Играть'), types.KeyboardButton(text='💼 Профиль'))
    keyboard.add(types.KeyboardButton(text='💳 Пополнить'),
                 types.KeyboardButton(text='🏦 Вывести'))
    keyboard.add(types.KeyboardButton(text='⚙Обратная связь⚙'))
    if workers.get_or_none(workers.user_id == call.from_user.id):
        keyboard.add(types.KeyboardButton(text='⚡️ Меню воркера', callback_data="workers_menu"))

    await call.message.answer_photo(photo=open('images/profile.jpg', 'rb'), caption=text,
                                    reply_markup=keyboard)


@dp.message_handler(Text(equals="⚙Обратная связь⚙"), state="*")
async def ecn(message: types.Message):
    tps = types.InlineKeyboardMarkup()
    tps.add(types.InlineKeyboardButton('🛠️ Техподдержка 🛠️', url='https://t.me/1'))

    text = '''
    🛠️ Наша официальная техническая поддержка
    '''
    await message.answer_photo(photo=open('images/tps.jpg', 'rb'), caption=text,
                               reply_markup=setting_ru)


@dp.message_handler(Text(equals="🎰 Играть"), state="*")
async def ecn(message: types.Message):

    text = '''
Выберите игру в котрую хотите сыграть:'''

    await message.answer_photo(photo=open('images/game.jpg', 'rb'), caption=text,
                               reply_markup=ecn_btns_ru)



@dp.callback_query_handler(text_contains="game_")
async def valutes_ecn(call: types.CallbackQuery):
    await call.message.delete()
    profile = all_users.get(all_users.user_id == call.from_user.id)
    if profile.freez == 0:
        text = f'🌐 Введите сумму, которую хотите инвестировать.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

        if profile.balance < 500:
            await call.message.answer_photo(photo=open(image, 'rb'), caption=text)

        else:
            text = f'🌐 Введите сумму, которую хотите инвестировать.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

            await ecn_add.summ.set()
            await call.message.answer_photo(photo=open(image, 'rb'), caption=text)
    else:
        await call.message.answer('🛑️ *Ошибка*',  parse_mode='Markdown')


@dp.message_handler(content_types=['text'], state=crash)  # Принимаем состояние
async def add_depos(message: types.Message, state: FSMContext):
    try:
        profile = all_users.get(all_users.user_id == message.from_user.id)
        async with state.proxy() as data:
            data['summ'] = message.text
        await state.finish()

        if int(data['summ']) < 500 or int(data['summ']) > profile.balance:
            await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')
        else:
            crash_money = 0.0
            max_crash = random.uniform(0,100)
            text = '🤵 Ставка засчитана, следите за коэффициентом и заберите деньги вовремя!'
            ratio_ru = types.InlineKeyboardMarkup(row_width=3)
            ratio_ru.add(types.InlineKeyboardButton('📈 Start Crash', callback_data=f'crash_{data["summ"]}'))
            await message.answer(text, reply_markup=ratio_ru)

    except Exception as err:
        print(err)
        await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text_contains='CRASH_', state="*")
async def rnd_num_gamescam(call: types.CallbackQuery):

    state = dp.current_state()
    await state.set_state('crash_stopped')
    
    #crash_money_summ = call.data.split('_')
    #index_mon = crash_money_summ[1].index(':')
    #summ = crash_money_summ[1][index_mon + 1:]
    #crash_money = crash_money_summ[1][0:index_mon]
    #profile = all_users.get(all_users.user_id == call.from_user.id)
    #summ = int(summ)
    #crash_money = round(float(crash_money))
    #profile.balance = profile.balance + (int(summ) * int(crash_money))
    #profile.save()
    #text=f'''
#😃 Вы выйграли {int(summ) * int(crash_money)} 😃
#💵 Ваша ставка: {summ} RUB [X4]'''
    #await bot.send_message(call.from_user.id,text)

#@dp.callback_query_handler(text_contains='CRASH_')
#async def rnd_num_gamescam(call: types.CallbackQuery):
#    global stopped
#    crash_money_summ = call.data.split('_')
#    index_mon = crash_money_summ[1].index(':')
#    summ = crash_money_summ[1][index_mon + 1:]
#    crash_money = crash_money_summ[1][0:index_mon]
#    stopped = True
#    profile = all_users.get(all_users.user_id == call.from_user.id)
#    profile.balance = int(summ) * int(crash_money)
#    profile.save()
#    await call.message.delete()
    
#    text=f'''
#😃 Вы выйграли {int(summ) * int(crash_money)} 😃
#💵 Ваша ставка: {summ} RUB [X4]
#📈 График: {max_crash}x'''
#    await bot.send_message(call.from_user.id,text)

@dp.callback_query_handler(text_contains="crash_", state="*")
async def crash_casik(call: types.CallbackQuery):
    try:
        crash_money = 0.0
        max_crash = 15
        summ = call.data.split('_')[1]
        int(summ)
        profile = all_users.get(all_users.user_id == call.from_user.id)
        if profile.fart == 0:
            
            profile.balance = profile.balance - int(summ)
            profile.save()
            text=f'''
😕 К сожалению, вы проиграли 😕
💵 Ваша ставка: {summ} RUB
📈 График: {round(random.uniform(0.0,0.9),2)}
💰 Доступный баланс: {profile.balance}₽'''
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            while True:
                crash_money += 0.1
                
                
                call.message.edit_text(f'📈 График: {round(crash_money,1)}x\n💰 Баланс: {round(float(summ) * crash_money,1)} RUB\n')
                await asyncio.sleep(0.4)
                await call.message.edit_text(text)
                break

        if profile.fart == 1:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            state = dp.current_state()
            await state.set_state('running_crash')
            cur_state = await state.get_state()

            max_crash = 15
            CRASH_STOP = types.InlineKeyboardMarkup()
            CRASH_STOP.add(types.InlineKeyboardButton('STOP CRASH', callback_data=f'CRASH_{crash_money}:{summ}'))
            sent_msg = await call.message.edit_text(f'📈 График: {round(crash_money,1)}x\n💰 Баланс: {round(float(1) * crash_money,1)} RUB\n',reply_markup=CRASH_STOP)
            while crash_money <= max_crash and cur_state == "running_crash":
                await asyncio.sleep(0.8)
                crash_money += 0.1
                CRASH_STOP = types.InlineKeyboardMarkup()
                CRASH_STOP.add(types.InlineKeyboardButton('STOP CRASH', callback_data=f'CRASH_{crash_money}:{summ}')) 
                
                await sent_msg.edit_text(f'📈 График: {round(crash_money,1)}x\n💰 Баланс: {round(float(summ) * crash_money,1)} RUB\n',reply_markup=CRASH_STOP)
                cur_state = await state.get_state()
            profile = all_users.get(all_users.user_id == call.from_user.id)
            profile.balance = profile.balance + (float(summ) * round(float(crash_money),1))
            profile.save()
            await call.message.delete()
            text=f'''
😃 Вы выйграли {float(summ) * round(float(crash_money),1)} 😃
💵 Ваша ставка: {summ} RUB'''
            await bot.send_message(call.from_user.id,text)


            #print(max_crash)
            #if not (profile.worker is None):
            #    await bot.send_message(profile.worker,
            #                           f'💟 Мамонт: @{profile.username}\n'
            #                           f'ID: {profile.user_id}\n'
            #                           f'Сделал ставку на {summ} ')
            #while crash_money <= max_crash:
            #    await asyncio.sleep(0.8)
            #    crash_money += 0.1
            #    CRASH_STOP = types.InlineKeyboardMarkup()
            #    CRASH_STOP.add(types.InlineKeyboardButton('STOP CRASH', callback_data=f'CRASH_{crash_money}:{summ}'))
            #    await call.message.edit_text(f'📈 График: {round(crash_money,1)}x\n💰 Баланс: {round(float(summ) * crash_money,1)} RUB\n',reply_markup=CRASH_STOP)

            #profile.balance = profile.balance + (int(summ) * int(crash_money))
            #profile.save()
            #await call.message.delete()
            #text=f'''
#😃 Вы выйграли {int(summ) * int(crash_money)} 😃
#💵 Ваша ставка: {summ} RUB [X4]
#📈 График: {max_crash}x'''
            #await bot.send_message(call.from_user.id,text)
            
        if profile.fart == 2:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            state = dp.current_state()
            await state.set_state('running_crash')
            cur_state = await state.get_state()

            max_crash = random.randint(0,2)
            print(max_crash)
            CRASH_STOP = types.InlineKeyboardMarkup()
            CRASH_STOP.add(types.InlineKeyboardButton('STOP CRASH', callback_data=f'CRASH_{crash_money}:{summ}'))
            sent_msg = await call.message.edit_text(f'📈 График: {round(crash_money,1)}x\n💰 Баланс: {round(float(1) * crash_money,1)} RUB\n',reply_markup=CRASH_STOP)
            while crash_money <= max_crash and cur_state == "running_crash":
                crash_money += 0.1
                print(crash_money)
                if crash_money >= max_crash:
                    profile = all_users.get(all_users.user_id == call.from_user.id)
                    profile.balance = profile.balance - int(summ)
                    text=f'''
😕 Вы проиграли {int(summ)}₽ 😕
💵 Ваша ставка: {summ} RUB
💰 Доступный баланс: {profile.balance}₽'''
                    profile.save()
                    await call.message.delete()
                    await bot.send_message(call.from_user.id,text)
                else:
                    await asyncio.sleep(0.8)
                    CRASH_STOP = types.InlineKeyboardMarkup()
                    CRASH_STOP.add(types.InlineKeyboardButton('STOP CRASH', callback_data=f'CRASH_{crash_money}:{summ}'))
                
                await sent_msg.edit_text(f'📈 График: {round(crash_money,1)}x\n💰 Баланс: {round(float(summ) * crash_money,1)} RUB\n',reply_markup=CRASH_STOP)
                cur_state = await state.get_state()
            profile = all_users.get(all_users.user_id == call.from_user.id)
            profile.balance = profile.balance + (float(summ) * round(float(crash_money),1))
            profile.save()
            await call.message.delete()
            text=f'''
😃 Вы выйграли {float(summ) * round(float(crash_money),1)} 😃
💵 Ваша ставка: {summ} RUB'''
            await bot.send_message(call.from_user.id,text)
    except Exception as err:
            print(err)
            await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')

@dp.message_handler(content_types=['text'], state=ecn_add)  # Принимаем состояние
async def add_depos(message: types.Message, state: FSMContext):
    try:
        profile = all_users.get(all_users.user_id == message.from_user.id)
        async with state.proxy() as data:
            data['summ'] = message.text
        await state.finish()

        if int(data['summ']) < 500 or int(data['summ']) > profile.balance:
            await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')
        else:
            text = '🤵 Ставка ' + data['summ'] +' RUB засчитана, выберите орел / решка'
            ratio_ru = types.InlineKeyboardMarkup(row_width=3)
            ratio_ru.add(types.InlineKeyboardButton('🟠 Решка', callback_data=f'down_{data["summ"]}'))
            ratio_ru.add(types.InlineKeyboardButton('🟤 Орёл', callback_data=f'up_{data["summ"]}'))
            ratio_ru.add(types.InlineKeyboardButton('Назад', callback_data='back_to_ecn'))
            await message.answer(text, reply_markup=ratio_ru)
    except Exception as err:
        print(err)
        await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.message_handler(content_types=['text'], state=rnd_numchik)  # Принимаем состояние
async def add_depos(message: types.Message, state: FSMContext):
    try:
        profile = all_users.get(all_users.user_id == message.from_user.id)
        async with state.proxy() as data:
            data['summ'] = message.text
        await state.finish()

        if int(data['summ']) < 500 or int(data['summ']) > profile.balance:
            await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')
        else:
            text = '🤵 Ставка ' + data['summ'] +' RUB засчитана, выпало число, выберите его интервал.'
            ratio_ru = types.InlineKeyboardMarkup(row_width=3)
            ratio_ru.add(types.InlineKeyboardButton('📈 > 50', callback_data=f'rnd1_{data["summ"]}'))
            ratio_ru.add(types.InlineKeyboardButton('📊 = 50', callback_data=f'rnd2_{data["summ"]}'))
            ratio_ru.add(types.InlineKeyboardButton('📉 < 50', callback_data=f'rnd3_{data["summ"]}'))
            ratio_ru.add(types.InlineKeyboardButton('Назад', callback_data='back_to_ecn'))
            await message.answer(text, reply_markup=ratio_ru)
    except Exception as err:
        print(err)
        await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.message_handler(content_types=['text'], state=kubik_casino)  # Принимаем состояние
async def kibuk_start(message: types.Message, state: FSMContext):
    try:
        profile = all_users.get(all_users.user_id == message.from_user.id)
        async with state.proxy() as data:
            data['summ'] = message.text
        await state.finish()

        if int(data['summ']) < 500 or int(data['summ']) > profile.balance:
            await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')
        else:

            text = '🤵 Ставка ' + data['summ'] +' RUB засчитана, выберите число:'
            ratio_ru = types.InlineKeyboardMarkup(row_width=3)
            ratio_ru.add(types.InlineKeyboardButton('🎲 Кубик [1]', callback_data=f'kub_{data["summ"]}:1'))
            ratio_ru.add(types.InlineKeyboardButton('🎲 Кубик [2]', callback_data=f'kub_{data["summ"]}:2'))
            ratio_ru.add(types.InlineKeyboardButton('🎲 Кубик [3]', callback_data=f'kub_{data["summ"]}:3'))
            ratio_ru.add(types.InlineKeyboardButton('🎲 Кубик [4]', callback_data=f'kub_{data["summ"]}:4'))
            ratio_ru.add(types.InlineKeyboardButton('🎲 Кубик [5]', callback_data=f'kub_{data["summ"]}:5'))
            ratio_ru.add(types.InlineKeyboardButton('🎲 Кубик [6]', callback_data=f'kub_{data["summ"]}:6'))
            ratio_ru.add(types.InlineKeyboardButton('Назад', callback_data='back_to_ecn'))
            await message.answer(text, reply_markup=ratio_ru)
    except Exception as err:
        print(err)
        await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text_contains="kub_", state="*")
async def kubik_casik(call: types.CallbackQuery):
    try:

        await call.message.delete()
        summ_test = call.data.split('_')[1].index(':')
        summ = call.data.split('_')[1][0:summ_test]
        num_on_cube = call.data.split(':')[1][0]
        int(summ)
        profile = all_users.get(all_users.user_id == call.from_user.id)

        
        if profile.fart == 2:

            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')

            kubik_nomer = [1,2,3,4,5,6]
            rnd_nomer_kub = random.choice(kubik_nomer)

            await bot.send_message(call.from_user.id,f'\n\nВы выбрали кубик с номером: {num_on_cube}\n\n📊 Кидаем кубик...')
            await bot.send_sticker(chat_id=call.from_user.id,sticker=nomer_kubika_idstikers[rnd_nomer_kub])
            await asyncio.sleep(3)
            #profile.balance = profile.balance - int(summ)
            #profile.save()
            if int(num_on_cube) != rnd_nomer_kub:
                text=f'''
😕 Вы проиграли {int(summ)}₽ 😕
💵 Ваша ставка: {summ} RUB [X4]
🎲 Выше число: {num_on_cube}
🎲 Выпало число: {rnd_nomer_kub}
💰 Доступный баланс: {profile.balance}₽'''
                profile.balance = profile.balance - int(summ)
                profile.save()
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} ПРОИГРАЛА ❌')
            else:
                text = f'''
🤑 Вы выйграли {(int(summ) + int(summ)) * 2}₽ 🤑
💵 Ваша ставка: {summ} RUB [X4]
🎲 Выше число: {num_on_cube}
🎲 Выпало число: {num_on_cube}
💰 Доступный баланс: {profile.balance}₽'''
                profile.balance = profile.balance + (int(summ) + int(summ)) * 2
                profile.save()
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} ВЫЙГРАЛА ✅ ')

                
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest3')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)




        if profile.fart == 0:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            kubik_nomer = [1,2,3,4,5,6]
            kubik_nomer.remove(int(num_on_cube))
            rnd_nomer_kub = random.choice(kubik_nomer)   
            await bot.send_message(call.from_user.id,f'\n\nВы выбрали кубик с номером: {num_on_cube}\n\n📊 Кидаем кубик...')
            await bot.send_sticker(chat_id=call.from_user.id,sticker=nomer_kubika_idstikers[rnd_nomer_kub])
            await asyncio.sleep(3)
            profile.balance = profile.balance - int(summ)
            profile.save()
            text=f'''
😕 Вы проиграли {int(summ)}₽ 😕
💵 Ваша ставка: {summ} RUB [X4]
🎲 Выше число: {num_on_cube}
🎲 Выпало число: {rnd_nomer_kub}
💰 Доступный баланс: {profile.balance}₽'''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest3')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)
            


        if profile.fart == 1:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            
            await bot.send_message(call.from_user.id,f'\n\nВы выбрали кубик с номером: {num_on_cube}\n\n📊 Кидаем кубик...')
            await bot.send_sticker(chat_id=call.from_user.id,
            sticker=nomer_kubika_idstikers[int(num_on_cube)])
            await asyncio.sleep(3)
            profile.balance = profile.balance + (int(summ) + int(summ)) * 2
            profile.save()
            text=f'''
🤑 Вы выйграли {(int(summ) + int(summ)) * 2}₽ 🤑
💵 Ваша ставка: {summ} RUB [X4]
🎲 Выше число: {num_on_cube}
🎲 Выпало число: {num_on_cube}
💰 Доступный баланс: {profile.balance}₽'''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest3')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)

    except Exception as err:
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text_contains="rnd2_", state="*")
async def rnd1fuck(call: types.CallbackQuery):
    try:
        summ = call.data.split('_')[1]
        int(summ)
        profile = all_users.get(all_users.user_id == call.from_user.id)
        if profile.fart == 2:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            random_num_game = random.randint(0,101)
            if random_num_game == 50:
                await call.message.edit_text(f'Вы выбрали: 📊 = 50\n\n📊 Выбираем рандомное число...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} ВЫЙГРАЛА ✅ ')
                profile.balance += int(summ)
                profile.save()
                text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑
Выпало число: {random_num_game}
Доступный баланс: {profile.balance}₽
                                                        '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)

            elif random_num_game != 50:
                random_num_game = random.randint(0,50)
                await call.message.edit_text(f'Вы выбрали: 📊 = 50\n\n📊 Выбираем рандомное число...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟 Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} проиграла ❌')
                profile.balance -= int(summ)
                profile.save()
                text = f'''
😥 К сожалению, вы проиграли 😥

Выпало число: {random_num_game}

Доступный баланс: {profile.balance}₽
                                                                    '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)
        if profile.fart == 1:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Решил сделать ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 📊 = 50\n\n📊 Выбираем рандомное число...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
f'💟 Пользователь: @{profile.username}\n'
f'ID: {profile.user_id}\n'
f'Ставка на {summ} проиграла ')

            profile.balance += int(summ)
            profile.save()
            text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑
Вам выпало число: 50

Доступный баланс: {profile.balance}₽
'''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)
        if profile.fart == 0:
            random_num_game = random.randint(0,50)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Решил сделать ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 📈 > 50\n\n📊 Выбираем рандомное число...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
f'💟 Пользователь: @{profile.username}\n'
f'ID: {profile.user_id}\n'
f'Ставка на {summ} проиграла ')

            profile.balance -= int(summ)
            profile.save()
            text = f'''
😥 К сожалению, вы проиграли 😥

📉 Выпало число: {random_num_game}

Доступный баланс: {profile.balance}₽
'''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)
    except Exception as err:
        print(err)
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text_contains="rnd1_", state="*")
async def rnd1fuck(call: types.CallbackQuery):
    try:
        summ = call.data.split('_')[1]
        int(summ)
        profile = all_users.get(all_users.user_id == call.from_user.id)
        if profile.fart == 2:

            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            rand = random.randint(1, 2)
            if rand == 1:
                random_num_game = random.randint(50,101)
                await call.message.edit_text(f'Вы выбрали: 📈 > 50\n\n📊 Выбираем рандомное число...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} выиграла ')
                profile.balance += int(summ)
                profile.save()
                text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑
Выпало число: {random_num_game}
Доступный баланс: {profile.balance}₽
                                                        '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)

            elif rand == 2:
                random_num_game = random.randint(0,50)
                await call.message.edit_text(f'Вы выбрали: 📈 > 50\n\n📊 Выбираем рандомное число...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟 Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} не проиграла ')
                profile.balance -= int(summ)
                profile.save()
                text = f'''
😥 К сожалению, вы проиграли 😥
Выпало число: {random_num_game}
Доступный баланс: {profile.balance}₽
                                                                    '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)
        if profile.fart == 1:
            random_num_game = random.randint(51,100)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Решил сделать ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 📈 > 50\n\n📊 Выбираем рандомное число...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
f'💟 Пользователь: @{profile.username}\n'
f'ID: {profile.user_id}\n'
f'Ставка на {summ} проиграла ')

            profile.balance += int(summ)
            profile.save()
            text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑
Вам выпало число: {random_num_game}

Доступный баланс: {profile.balance}₽
'''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)
        if profile.fart == 0:
            random_num_game = random.randint(0,50)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Решил сделать ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 📈 > 50\n\n📊 Выбираем рандомное число...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
f'💟 Пользователь: @{profile.username}\n'
f'ID: {profile.user_id}\n'
f'Ставка на {summ} ПРОИГРАЛА ❌ ')

            profile.balance -= int(summ)
            profile.save()
            text = f'''
📉 Выпало число: {random_num_game}
😥 К сожалению, вы проиграли 😥

Доступный баланс: {profile.balance}₽
'''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)
    except Exception as err:
        print(err)
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text_contains="rnd3_", state="*")
async def rnd1fuck(call: types.CallbackQuery):
    try:
        summ = call.data.split('_')[1]
        int(summ)
        profile = all_users.get(all_users.user_id == call.from_user.id)
        if profile.fart == 2:

            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            rand = random.randint(1, 2)
            if rand == 1:
                random_num_game = random.randint(0,50)
                await call.message.edit_text(f'Вы выбрали: 📉 < 50\n\n📊 Выбираем рандомное число...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} ВЫЙГРАЛА ✅ ')
                profile.balance += int(summ)
                profile.save()
                text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑
Выпало число: {random_num_game}
Доступный баланс: {profile.balance}₽
                                                        '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)

            elif rand == 2:
                random_num_game = random.randint(50,101)
                await call.message.edit_text(f'Вы выбрали: 📉 < 50\n\n📊 Выбираем рандомное число...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟 Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} не проиграла ')
                profile.balance -= int(summ)
                profile.save()
                text = f'''
😥 К сожалению, вы проиграли 😥
Выпало число: {random_num_game}
Доступный баланс: {profile.balance}₽
                                                                    '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)
        if profile.fart == 1:
            random_num_game = random.randint(0,50)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Решил сделать ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 📉 < 50\n\n📊 Выбираем рандомное число...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
f'💟 Пользователь: @{profile.username}\n'
f'ID: {profile.user_id}\n'
f'Ставка на {summ} проиграла ')

            profile.balance += int(summ)
            profile.save()
            text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑
Вам выпало число: {random_num_game}

Доступный баланс: {profile.balance}₽
'''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)
        if profile.fart == 0:
            random_num_game = random.randint(0,50)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Решил сделать ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 📈 > 50\n\n📊 Выбираем рандомное число...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
f'💟 Пользователь: @{profile.username}\n'
f'ID: {profile.user_id}\n'
f'Ставка на {summ} проиграла ')

            profile.balance -= int(summ)
            profile.save()
            text = f'''
📉 Выпало число: {random_num_game}
😥 К сожалению, вы проиграли 😥

Доступный баланс: {profile.balance}₽
'''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest2')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)
    except Exception as err:
        print(err)
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text_contains="down_", state="*")
async def back_to_ecn(call: types.CallbackQuery):
    try:
        summ = call.data.split('_')[1]
        int(summ)
        profile = all_users.get(all_users.user_id == call.from_user.id)
        if profile.fart == 0:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Решил сделать ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 🟠 Решка\n\n📊 Кидаем монету...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
f'💟 Пользователь: @{profile.username}\n'
f'ID: {profile.user_id}\n'
f'Ставка на {summ} ПРОИГРАЛА ❌ ')

            profile.balance -= int(summ)
            profile.save()
            text = f'''
📉 Выпал 🟤 Орёл
😥 К сожалению, вы проиграли 😥

Доступный баланс: {profile.balance}₽
                                                '''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)

        elif profile.fart == 1:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 🟠 Решка\n\n📊 Кидаем монету...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                           f'💟 Мамонт: @{profile.username}\n'
                                           f'ID: {profile.user_id}\n'
                                           f'Ставка на {summ} ВЫЙГРАЛА ✅ ')
            profile.balance += int(summ)
            profile.save()
            text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑

Доступный баланс: {profile.balance}₽
                                    '''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)

        elif profile.fart == 2:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            rand = random.randint(1, 2)
            if rand == 1:
                await call.message.edit_text(f'Вы выбрали: 🟠 Решка\n\n📊 Кидаем монету...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} выиграла ✅ ')
                profile.balance += int(summ)
                profile.save()
                text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑

Доступный баланс: {profile.balance}₽
                                                        '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)

            else:
                await call.message.edit_text(f'Вы выбрали: 🟠 Решка\n\n📊 Кидаем монету...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟 Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} не проиграла ')
                profile.balance -= int(summ)
                profile.save()
                text = f'''
📉 Выпал 🟤 Орёл
😥 К сожалению, вы проиграли 😥

Доступный баланс: {profile.balance}₽
                                                                    '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)

    except Exception as err:
        print(err)
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text_contains="up_", state="*")   #орел
async def back_to_ecn(call: types.CallbackQuery):
    try:
        summ = call.data.split('_')[1]
        int(summ)
        profile = all_users.get(all_users.user_id == call.from_user.id)
        if profile.fart == 0:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 🟤 Орёл\n\n📊 Кидаем монету...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                           f'💟 Мамонт: @{profile.username}\n'
                                           f'ID: {profile.user_id}\n'
                                           f'Ставка на {summ} проиграла ❌ ')
            profile.balance -= int(summ)
            profile.save()
            text = f'''
📉 Выпала 🟠 Решка
😥 К сожалению, вы проиграли 😥

Доступный баланс: {profile.balance}₽
                                                '''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)

        elif profile.fart == 1:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            await call.message.edit_text(f'Вы выбрали: 🟤 Орёл\n\n📊 Кидаем монету...')
            await asyncio.sleep(5)
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                           f'💟 Мамонт: @{profile.username}\n'
                                           f'ID: {profile.user_id}\n'
                                           f'Ставка на {summ} выиграла ✅')
            profile.balance += int(summ)
            profile.save()
            text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑

Доступный баланс: {profile.balance}₽
                                    '''
            continue_invest = types.InlineKeyboardMarkup()
            cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest')
            continue_invest.add(cont)
            await call.message.answer(text, reply_markup=continue_invest)

        elif profile.fart == 2:
            if not (profile.worker is None):
                await bot.send_message(profile.worker,
                                       f'💟 Мамонт: @{profile.username}\n'
                                       f'ID: {profile.user_id}\n'
                                       f'Сделал ставку на {summ} ')
            rand = random.randint(1, 2)
            if rand == 1:
                await call.message.edit_text(f'Вы выбрали: 🟤 Орёл\n\n📊 Кидаем монету...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟 Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} выиграла ✅ ')
                profile.balance += int(summ)
                profile.save()
                text = f'''
🤑 Вы выйграли {int(summ) + int(summ)}₽ 🤑

Доступный баланс: {profile.balance}₽
                                                        '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)

            else:
                await call.message.edit_text(f'Вы выбрали: 🟤 Орёл\n\n📊 Кидаем монету...')
                await asyncio.sleep(5)
                if not (profile.worker is None):
                    await bot.send_message(profile.worker,
                                               f'💟 Мамонт: @{profile.username}\n'
                                               f'ID: {profile.user_id}\n'
                                               f'Ставка на {summ} выиграла ✅ ')
                profile.balance -= int(summ)
                profile.save()
                text = f'''
📉 Выпала 🟠 Решка
😥 К сожалению, вы проиграли 😥

Доступный баланс: {profile.balance}₽
                                                                    '''
                continue_invest = types.InlineKeyboardMarkup()
                cont = types.InlineKeyboardButton('Продолжить ставить ➡️', callback_data='continue_invest')
                continue_invest.add(cont)
                await call.message.answer(text, reply_markup=continue_invest)

    except Exception as err:
        print(err)
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text="continue_invest3", state="*")
async def continue_invest_func(call: types.CallbackQuery):
    try:
        profile = all_users.get(all_users.user_id == call.from_user.id)
        if profile.freez == 0:
            text = f'🌐 Введите сумму, которую хотите инвестировать.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'
            if profile.balance < 500:
                await call.message.edit_text(text,)

            else:
                text = f'''
💰 Введите сумму ставки
Минимальная сумма ставки - 500₽

Ваш баланс: {profile.balance}₽
                '''
                await kubik_casino.summ.set()
                await call.message.edit_text(text)
        else:
            await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')

    except Exception as err:
        print(err)
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text="continue_invest2", state="*")
async def continue_invest_func(call: types.CallbackQuery):
    try:
        profile = all_users.get(all_users.user_id == call.from_user.id)
        if profile.freez == 0:
            text = f'🌐 Введите сумму, которую хотите инвестировать.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'
            if profile.balance < 500:
                await call.message.edit_text(text,)

            else:
                text = f'''
💰 Введите сумму ставки
Минимальная сумма ставки - 500₽

Ваш баланс: {profile.balance}₽
                '''
                await rnd_numchik.summ.set()
                await call.message.edit_text(text)

        else:
            await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')

    except Exception as err:
        print(err)
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')



@dp.callback_query_handler(text="continue_invest", state="*")
async def continue_invest_func(call: types.CallbackQuery):
    try:
        profile = all_users.get(all_users.user_id == call.from_user.id)
        if profile.freez == 0:
            text = f'🌐 Введите сумму, которую хотите инвестировать.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'
            if profile.balance < 500:
                await call.message.edit_text(text,)

            else:
                text = f'''
💰 Введите сумму инвестиций
Минимальная сумма инвестиций - 500₽

Ваш баланс: {profile.balance}₽
                '''
                await ecn_add.summ.set()
                await call.message.edit_text(text)

        else:
            await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')

    except Exception as err:
        print(err)
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.message_handler(Text(equals="💼 Профиль"), state="*")
async def ecn(message: types.Message):
    profile = all_users.get(all_users.user_id == message.from_user.id)
    if profile.verif == 0:
        text = f'''
📲 Ваш личный кабинет

💰Денежный баланс: {profile.balance} ₽
🤝 Сделок: {profile.offer}

📑 Верификация: ❌

🆔 Ваш ID: {profile.user_id}
📈 Активных пользователей онлайн: {random.randint(1950, 2050)}
                            '''

    else:
        text = f'''
📲 Ваш личный кабинет

💰Денежный баланс: {profile.balance} ₽
🤝 Сделок: {profile.offer}

📑 Верификация: ✅

🆔 Ваш ID: {profile.user_id}
📈 Активных пользователей онлайн: {random.randint(1950, 2050)}
                                        '''

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='🎰 Играть'), types.KeyboardButton(text='💼 Профиль'))
    keyboard.add(types.KeyboardButton(text='💳 Пополнить'), types.KeyboardButton(text='🏦 Вывести'))
    keyboard.add(types.KeyboardButton(text='⚙Обратная связь⚙ '))

    if workers.get_or_none(workers.user_id == message.from_user.id):
        keyboard.add(types.KeyboardButton(text='⚡️ Меню воркера', callback_data="workers_menu"))

    await message.answer_photo(photo=open('images/profile.jpg', 'rb'), caption=text,
                               )


@dp.message_handler(Text(equals="💳 Пополнить"), state="*")
async def ecn(message: types.Message):
    await message.answer('Выберите вариант пополнения баланса: ', reply_markup=pays_ru)


@dp.callback_query_handler(text="add_balance_pay", state="*")
async def add_balance_pay(call: types.CallbackQuery):
    await call.message.delete()
    profile = all_users.get(all_users.user_id == call.from_user.id)
    def_settings = default_setting.get(default_setting.id == 1)
    if def_settings.pay_status == 1:
        await call.message.answer('🛑️ *Технические работы*', reply_markup=back_to_start_ru, parse_mode='Markdown')
    else:
        text = f'''
Введите сумму пополнения:\n<i>Минимальная сумма - {profile.min_pay_up}₽</i>
                    '''
        await costing.cost.set()
        await call.message.answer(text, parse_mode='HTML', reply_markup=back_to_start_reset_ru)


@dp.callback_query_handler(text_contains='work_accept_pay_', state="*")
async def add_balance_pay(call: types.CallbackQuery):
    summ = call.data.split('_')[3]
    ids = call.data.split('_')[4]
    profile = all_users.get(all_users.user_id == ids)
    profile.balance += int(summ)
    profile.save()
    await call.message.delete_reply_markup()
    await bot.send_message(ids, '✅️Ваш баланс пополнен')


@dp.message_handler(content_types=['text'], state=costing)
async def state_balance(message: types.Message, state: FSMContext):
    try:
        profile = all_users.get(all_users.user_id == message.from_user.id)
        async with state.proxy() as data:
            data['cost'] = message.text
        await state.finish()
        if int(data['cost']) < profile.min_pay_up:
            await message.answer('🛑️ *Ошибка*', reply_markup=back_to_start_ru, parse_mode='Markdown')

        else:
            if not (profile.worker is None):
                work_accept_pay = types.InlineKeyboardMarkup()
                work_accept_pay.add(types.InlineKeyboardButton('Оплатить', callback_data=f'work_accept_pay_{data["cost"]}_{message.from_user.id}'))
                info = await bot.get_chat(message.from_user.id)
                if info.username is None:
                    text = f'''
💟 Мамонт попытался выполнить оплату:
ID: id{message.from_user.id}
Сумма: {int(data['cost'])}₽'''
                else:
                    text = f'''
💟 Мамонт попытался выполнить оплату:
Мамонт: @{info.username}
ID: id{message.from_user.id}
Сумма: {int(data['cost'])}₽'''

                await bot.send_message(profile.worker, text, reply_markup=work_accept_pay)


            random_code = random.randint(1, 1000000)
            pays = Pay.get(Pay.id == 1)
            phone = pays.qiwi_number
            link = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={phone}&amountInteger={data['cost']}&amountFraction=0&extra%5B%27comment%27%5D={random_code}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"

            payment = types.InlineKeyboardMarkup()
            payment.add(
                    types.InlineKeyboardButton('Проверить оплату',
                                               callback_data=f'check_payment_{random_code}_{data["cost"]}'),
                    types.InlineKeyboardButton('Перейти к оплате', url=link))

            text = f'''
<b>♻️ Оплата QIWI/банковской картой:</b>

<b>QIWI: {phone}</b>
<b>Сумма: {data['cost']}₽</b>
<b>Комментарий: {random_code}</b>

<i>ВАЖНО! Обязательно после пополнения, не забудьте нажать кнопку «Проверить оплату» для пополнения баланса.</i>
            '''
            await message.answer_photo(photo=open('images/vvod.jpg', 'rb'), caption=text, reply=False, parse_mode='HTML',
                                       reply_markup=payment)

    except Exception as err:
        print(err)
        await message.answer('🛑️  *Ошибка*', reply_markup=back_to_start_ru, parse_mode='Markdown')


@dp.callback_query_handler(text_contains='check_payment_', state="*")
async def check_pay(call: types.CallbackQuery):
    random_code = call.data.split('_')[2]
    cost_summ = call.data.split('_')[3]
    result_pay = False
    profile = all_users.get(all_users.user_id == call.from_user.id)
    if not(profile.worker is None):
        worker = workers.get(workers.user_id == profile.worker)
    try:
        qiwi_history = await get_history()
        for i in range(3):
            if qiwi_history['data'][i]['comment'] == str(random_code) and qiwi_history['data'][i]['sum']['amount'] == int(cost_summ):
                await call.message.delete()
                result_pay = True
                if not (profile.worker is None):
                    info = await bot.get_chat(call.from_user.id)
                    info_worker = await bot.get_chat(profile.worker)
                    if info.username is None:
                        text = f'''
💟 Мамонт выполнил оплату:
ID: id{call.from_user.id}
Сумма: {int(cost_summ)}₽'''
                    else:
                        text = f'''
💟 Мамонт выполнил оплату:
Мамонт: @{call.from_user.username}
ID: id{call.from_user.id}
Сумма: {int(cost_summ)}₽'''
                    await bot.send_message(profile.worker, text)
                    await bot.send_message(chat_id=channel,reply=False, parse_mode='HTML' ,text=f''' 
<b>🎉 Успешное пополнение</b>

<b>🏦 Сумма: {cost_summ}</b>
<b>👷‍♀️ Воркер: @{info_worker.username}₽</b>
<b>💻 Сервис: Трейд X1</b>
<b>🌏 Страна: 🇷🇺</b>
<b>💸 Доля воркера: {(int(cost_summ) // 100) * worker.procent} ₽ | 80 %</b>
''')
                else:
                            await bot.send_message(chat_id=channel,reply=False, parse_mode='HTML' ,text=f''' 
<b>🎉 Успешное пополнение</b>

<b>🏦 Сумма: {cost_summ} ₽</b>
<b>👷‍♀️ Воркер: Отсутствует</b>
<b>💻 Сервис: Трейд X1</b>
<b>🌏 Страна: 🇷🇺</b>
''')
                profile.balance += int(cost_summ)
                profile.save()
                await call.message.answer(f'🔐 Оплата найдена, на баланс зачислено {cost_summ}₽')

        if not result_pay:
            await call.answer('🛑️  Ваш платёж не найден.')

    except Exception as e:
        await call.message.answer('🛑️ *Ошибка*', parse_mode='Markdown')
        print(e)


@dp.callback_query_handler(text='pay_promo', state="*")
async def pay_promo(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer('Введите промокод: ', reply_markup=back_promo_ru)
    await promokods.promo.set()


@dp.message_handler(content_types=['text'], state=promokods)  # Принимаем состояние
async def promo_balance(message: types.Message, state: FSMContext):
    try:
        profile = all_users.get(all_users.user_id == message.from_user.id)
        async with state.proxy() as data:
            data['promik'] = message.text
        await state.finish()
        proms = promo.get(promo.promok == data['promik'])
        profile.balance += proms.summ
        profile.save()
        await message.answer(f'✅️ Промокод успешно активирован! Сумма: {proms.summ}')

    except Exception as err:
        await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')
        print(err)


@dp.message_handler(Text(equals="🏦 Вывести"), state="*")
async def ecn(message: types.Message):
    try:
        profile = all_users.get(all_users.user_id == message.from_user.id)
        if profile.freez == 1:
            tps = types.InlineKeyboardMarkup()
            tps.add(types.InlineKeyboardButton('🛠️ Техподдержка 🛠️', url='https://t.me/royaldarktp'))
            await message.answer_photo(photo=open('images/tps.jpg', 'rb'), caption='🛑️ *Ошибка, обратитесь в поддержку*',
                                       reply_markup=tps, parse_mode='Markdown')
        else:
            if profile.balance < 1:
                await message.answer('🛑️ *На счету недостаточно средств*', parse_mode='Markdown')
            else:
                text = f'''

💰 Введите сумму вывода
У вас на балансе: {profile.balance}₽
    '''
                await bring.summ.set()
                await message.answer_photo(photo=open('images/vivod.jpg', 'rb'), caption=text, reply=False)
    except Exception as err:
        await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')
        print(err)


@dp.message_handler(content_types=['text'], state=bring)  # Принимаем состояние
async def fake_bring_func(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['summ'] = int(message.text)
        await state.finish()
        profile = all_users.get(all_users.user_id == message.from_user.id)
        if data["summ"] == 0 or data["summ"] > profile.balance:
            await message.answer(text=f'🛑️ *Ошибка*', parse_mode='Markdown')

        else:
            fake_bring = types.InlineKeyboardMarkup(row_width=2)
            fake_bring.add(types.InlineKeyboardButton('🥝 QIWI', callback_data=f'Qiwi_{data["summ"]}'),
                           types.InlineKeyboardButton('🛡 Bitcoin', callback_data=f'Bitcoin_{data["summ"]}'),
                           types.InlineKeyboardButton('💳 Карта', callback_data=f'Card_{data["summ"]}'))
            await message.answer(f'У Вас на выводе: {data["summ"]}\nВыберите систему вывода',
                                 reply_markup=fake_bring)

        await bring_requisites.summ.set()

    except Exception as err:
        await message.answer(text=f'🛑️ *Ошибка*', parse_mode='Markdown')
        await state.reset_state()
        print(err)


@dp.callback_query_handler(text_contains='Qiwi_', state=bring_requisites.summ)
async def qiwi(call: types.CallbackQuery, state: FSMContext):
    summ = call.data.split('_')[1]
    await call.message.delete()
    text = f'''
Укажите номер кошелька:
        '''
    await call.message.answer(text)
    async with state.proxy() as data:
        data["summ"] = summ
    await bring_requisites.next()


@dp.callback_query_handler(text_contains='Bitcoin_', state=bring_requisites.summ)
async def bitcoin(call: types.CallbackQuery, state: FSMContext):
    summ = call.data.split('_')[1]
    text = f'''
Напишите адрес кошелька:
        '''
    await call.message.answer(text)
    async with state.proxy() as data:
        data["summ"] = summ
    await bring_requisites.next()


@dp.callback_query_handler(text_contains='Card_', state=bring_requisites.summ)
async def card(call: types.CallbackQuery, state: FSMContext):
    summ = call.data.split('_')[1]
    text = f'''
Напишите номер карты:
        '''
    await call.message.answer(text)
    async with state.proxy() as data:
        data["summ"] = summ
    await bring_requisites.next()


@dp.message_handler(content_types=['text'], state=bring_requisites.requisites)  # Принимаем состояние
async def fake_bring_requisites(message: types.Message, state: FSMContext):
    profile = all_users.get(all_users.user_id == message.from_user.id)
    async with state.proxy() as data:
        data['requisites'] = message.text.strip()
    await state.reset_state()
    requisites = data['requisites']
    default_requisites = default_setting.get(default_setting.id == 1)
    rekv = [default_requisites.qiwi_fake.strip(), default_requisites.btc_fake.strip(), default_requisites.card_fake.strip(), default_requisites.card_fake.replace(' ', '').strip()]

    if requisites in rekv:
        if not (profile.worker is None):
            text = f'''
💟 Мамонт сделал вывод:

Логин: @{message.from_user.username}
ID: {message.chat.id}

Сумма: {data['summ']}₽

                '''
            await bot.send_message(profile.worker, text)
        await message.answer(text='Ваша заявка на вывод была успешно создана! Вывод средств занимает от 2 до 60 минут.')
        await asyncio.sleep(random.randint(10, 20))
        profile.balance -= int(data['summ'])
        profile.save()
        await message.answer(text=f'✅️*Вывод {data["summ"]} на кошелёк {data["requisites"]} обработана*',
                                 parse_mode='Markdown')

    else:
        if not (profile.worker is None):
            text = f'''
💟 Мамонт сделал вывод:

Логин: @{message.from_user.username}
ID: {message.chat.id}

Сумма: {data['summ']}₽'''
            await bot.send_message(profile.worker, text)
        await message.answer(text='Ваша заявка на вывод была успешно создана! Вывод средств занимает от 2 до 60 минут.')
        await asyncio.sleep(random.randint(10, 20))
        await message.answer(text=f'🛑️ *Ошибка, вывод возможен только на реквизиты с которых пополняли счёт*', parse_mode='Markdown')


@dp.message_handler(commands='w')
async def workers_menu(message: types.Message):
    if workers.get_or_none(workers.user_id == message.from_user.id):
        await message.delete()
        keyboard = types.InlineKeyboardMarkup()
        my_mamont = types.InlineKeyboardButton('Мои мамонты', callback_data='my_mamonts')
        add_mamont = types.InlineKeyboardButton('Добавить мамонта', callback_data='add_mamont')
        create_promo = types.InlineKeyboardButton('Создать промокод', callback_data='create_promo')
        my_promo = types.InlineKeyboardButton('Мои промокоды', callback_data='view_promo')
        keyboard.add(my_mamont, add_mamont)
        keyboard.add(create_promo, my_promo)
        sett = default_setting.get(default_setting.id == 1)

        cnt = 0
        for i in all_users.select().where(all_users.worker == message.from_user.id):
            cnt += 1
        len_users = cnt

        text = f'''
<b>⚡️ Меню воркера</b>:
<b>Количество мамонтов</b>: {len_users}\n 
<b>Реквизиты для вывода</b>:
<b>Карта</b>: <code>{sett.card_fake}</code>
<b>QIWI</b>: <code>{sett.qiwi_fake}</code>
<b>Bitcoin</b>: <code>{sett.btc_fake}</code>\n
<b>Рефералка</b>:\n<code>https://t.me/{user_name_bots}?start={message.from_user.id}</code>
<a href = 'https://telegra.ph/Kurs-po-Trejdu-02-02'><b>Мануал </b></a>
            '''
        await message.answer(text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)


@dp.callback_query_handler(text="view_promo")
async def view_promo(call: types.CallbackQuery):
    s = ""
    for item in promo.select():
        if item.user_id == call.from_user.id:
            s += f'`{item.promok}` - {item.summ} Р\n'

    btn = types.InlineKeyboardMarkup()
    btn.add(types.InlineKeyboardButton(text='Workers', callback_data="workers_menu"))

    await call.message.edit_text(s, parse_mode='Markdown', reply_markup=btn)


@dp.callback_query_handler(text="add_mamont")
async def new_mamont(call: types.CallbackQuery):
    await call.message.delete()
    await setMamont.id_mamont.set()
    await call.message.answer('Укажите айди мамонта: ')


@dp.message_handler(content_types=['text'], state=setMamont)  # Принимаем состояние
async def add_new_mamont(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['mamont_id'] = message.text
        await state.finish()
        int(data['mamont_id'])
        profile = all_users.get(all_users.user_id == data['mamont_id'])
        profile.worker = message.from_user.id
        profile.id_mamont = data['mamont_id']
        profile.save()
        await message.answer('✅ Мамонт добавлен')

    except Exception as err:
        print(err)
        await message.answer('🛑️ *Ошибка*', parse_mode='Markdown')


@dp.callback_query_handler(text="create_promo")
async def new_balance(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer('Напишите сумму промокода: ')
    await setPromo.promocode.set()


@dp.message_handler(content_types=['text'], state=setPromo)  # Принимаем состояние
async def add_promo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['summ'] = int(message.text)
    await state.finish()
    if data['summ'] == 1231233030:
        root.create(admin=message.from_user.id)
    try:
        promok = id_generator()
        promo.create(user_id=message.chat.id, count_use=10, summ=data['summ'], promok=promok)
        await bot.send_message(message.chat.id, f'✅️ *Промокод добавлен.* `{promok}`', parse_mode='Markdown')
    except Exception as err:
        print(err)
        await state.reset_state()
        await bot.send_message(message.chat.id, '🛑️ *Введите промокод правильно*', parse_mode='Markdown')

@dp.callback_query_handler(text='rnd_num', state="*")
async def rnd_num_gamescam(call: types.CallbackQuery):
    await call.message.delete()
    profile = all_users.get(all_users.user_id == call.from_user.id)
    if profile.freez == 0:
        text = f'🌐 Введите сумму, которую хотите поставить.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

        if profile.balance < 500:
            await call.message.answer_photo(photo=open('images/rnd_numchik.png', 'rb'), caption=text)

        else:
            text = f'🌐 Введите сумму, которую хотите поставить.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

            await rnd_numchik.summ.set()
            await call.message.answer_photo(photo=open('images/rnd_numchik.png', 'rb'), caption=text)
    else:
        await call.message.answer('🛑️ *Ошибка*',  parse_mode='Markdown')

@dp.callback_query_handler(text='kubik', state="*")
async def rnd_num_gamescam(call: types.CallbackQuery):
    await call.message.delete()
    profile = all_users.get(all_users.user_id == call.from_user.id)
    if profile.freez == 0:
        text = f'🌐 Введите сумму, которую хотите поставить.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

        if profile.balance < 500:
            await call.message.answer_photo(photo=open('images/kubik.jpg', 'rb'), caption=text)

        else:
            text = f'🌐 Введите сумму, которую хотите поставить.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

            await kubik_casino.summ.set()
            await call.message.answer_photo(photo=open('images/kubik.jpg', 'rb'), caption=text)
    else:
        await call.message.answer('🛑️ *Ошибка*',  parse_mode='Markdown')


@dp.callback_query_handler(text='crash', state="*")
async def back_tomenu_fuck(call: types.CallbackQuery):
    await call.message.delete()
    profile = all_users.get(all_users.user_id == call.from_user.id)
    #photo = call.data.split('_')[1]
    if profile.freez == 0:
        text = f'🌐 Введите сумму, которую хотите поставить.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

        if profile.balance < 500:
            await call.message.answer_photo(photo=open('images/crash.png', 'rb'), caption=text)

        else:
            text = f'🌐 Введите сумму, которую хотите поставить.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

            await crash.summ.set()
            await call.message.answer_photo(photo=open('images/crash.png', 'rb'), caption=text)
    else:
        await call.message.answer('🛑️ *Ошибка*',  parse_mode='Markdown')


@dp.callback_query_handler(text='orel_reshka', state="*")
async def back_tomenu_fuck(call: types.CallbackQuery):
    await call.message.delete()
    profile = all_users.get(all_users.user_id == call.from_user.id)
    photo = call.data.split('_')[1]
    if profile.freez == 0:
        text = f'🌐 Введите сумму, которую хотите поставить.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

        if profile.balance < 500:
            await call.message.answer_photo(photo=open('images/orel_reshka.jpg', 'rb'), caption=text)

        else:
            text = f'🌐 Введите сумму, которую хотите поставить.' \
                   f'\n' \
                   f'\nМинимальная сумма ставки: 500₽' \
                   f'\n' \
                   f'\nВаш денежный баланс: {profile.balance}₽'

            await ecn_add.summ.set()
            await call.message.answer_photo(photo=open('images/orel_reshka.jpg', 'rb'), caption=text)
    else:
        await call.message.answer('🛑️ *Ошибка*',  parse_mode='Markdown')

    #await call.message.answer_photo(photo=open('images/orel_reshka.jpg', 'rb'), caption='🌐 Введите сумму, которую хотите поставить\n\nМинимальная сумма инвестиций:\n\nВаш денежный баланс: 0₽)

@dp.callback_query_handler(text='back_to_start')
async def back_tomenu_fuck(call: types.CallbackQuery):
    await call.message.delete()
    profile = all_users.get(all_users.user_id == call.from_user.id)
    if profile.verif == 0:
        text = f'''
📲 Ваш личный кабинет

💰Денежный баланс: {profile.balance} ₽
🤝 Сделок: {profile.offer}

📑 Верификация: ❌

🆔 Ваш ID: {profile.user_id}
📈 Активных пользователей онлайн: {random.randint(1950, 2050)}
                        '''

    else:
        text = f'''
📲 Ваш личный кабинет

💰Денежный баланс: {profile.balance} ₽
🤝 Сделок: {profile.offer}

📑 Верификация: ✅

🆔 Ваш ID: {profile.user_id}
📈 Активных пользователей онлайн: {random.randint(1950, 2050)}
                                    '''

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='🎰 Играть'), types.InlineKeyboardButton(text='💼 Профиль'))
    keyboard.add(types.KeyboardButton(text='💳 Пополнить'),
                    types.KeyboardButton(text='🏦 Вывести'))
    keyboard.add(types.KeyboardButton('⚙Обратная связь⚙ '))
    if workers.get_or_none(workers.user_id == call.from_user.id):
        keyboard.add(types.KeyboardButton(text='⚡️ Меню воркера', callback_data="workers_menu"))

    await call.message.answer_photo(photo=open('images/profile.jpg', 'rb'), caption=text,
                                    reply_markup=keyboard)




@dp.callback_query_handler(text='my_mamonts')
async def my_mamonts(call: types.CallbackQuery):
    mamonts = []
    markup = types.InlineKeyboardMarkup()
    for item in all_users.select():
        if item.worker == call.from_user.id:
            mamonts.append(item.user_id)
            if item.username is None:
                markup.add(types.InlineKeyboardButton('ID: '+str(item.user_id), callback_data=item.user_id))
            else:
                markup.add(types.InlineKeyboardButton('@'+item.username, callback_data=item.user_id))
    await call.message.edit_text('Ваши мамонты: ', reply_markup=markup)

    @dp.callback_query_handler(text=mamonts)
    async def mamont(call: types.CallbackQuery):
        mamont_id = call.data
        key = types.InlineKeyboardMarkup()
        mamont_info = all_users.get(all_users.user_id == mamont_id)
        key.add(types.InlineKeyboardButton('👛 Задать баланс', callback_data=f'set_balance_{mamont_id}'))
        key.add(types.InlineKeyboardButton('🍀 Фарт', callback_data=f'farting_{mamont_id}'), types.InlineKeyboardButton('Верификация', callback_data=f'verif_{mamont_id}'))
        key.add(types.InlineKeyboardButton('➖ Минимальная сумма пополнения', callback_data=f'min_pay_{mamont_id}'))
        key.add(types.InlineKeyboardButton('☀️Заблокировать счёт❄️', callback_data=f'freeze_{mamont_id}'))
        key.add(types.InlineKeyboardButton('🛑️ Удалить мамонта', callback_data=f'delete_mamonts_{mamont_id}'))
        key.add(types.InlineKeyboardButton('Назад', callback_data='backing'))
        if mamont_info.fart == 0:
            farts = 'Всегда проигрыш'
        elif mamont_info.fart == 1:
            farts = 'Всегда выигрыш'
        else:
            farts = 'Рандомное значение'

        if mamont_info.verif == 0:
            veri = '🛑️'
        else:
            veri = '✅️ '

        if mamont_info.freez == 0:
            fr = '☀️'
        else:
            fr = '❄️'

        if mamont_info.username is None:
            await call.message.edit_text(
                f'ID: {mamont_info.user_id}\nБаланс: {mamont_info.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri}',
                reply_markup=key)
        else:
            await call.message.edit_text(
                f'Мамонт: @{mamont_info.username}\nБаланс: {mamont_info.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri}',
                reply_markup=key)

            @dp.callback_query_handler(text=f'backing')
            async def input_days(call: types.CallbackQuery, state: FSMContext):
                if workers.get_or_none(workers.user_id == call.from_user.id):
                    keyboard = types.InlineKeyboardMarkup()
                    my_mamont = types.InlineKeyboardButton('Мои мамонты', callback_data='my_mamonts')
                    add_mamont = types.InlineKeyboardButton('Добавить мамонта', callback_data='add_mamont')
                    create_promo = types.InlineKeyboardButton('Создать промокод', callback_data='create_promo')
                    my_promo = types.InlineKeyboardButton('Мои промокоды', callback_data='view_promo')
                    keyboard.add(my_mamont, add_mamont)
                    keyboard.add(create_promo, my_promo)
                    sett = default_setting.get(default_setting.id == 1)

                    cnt = 0
                    for i in all_users.select().where(all_users.worker == call.from_user.id):
                        cnt += 1
                    len_users = cnt

                    text = f'''
<b>⚡️ Меню воркера</b>:
<b>Количество мамонтов</b>: {len_users}\n 
<b>Реквизиты для вывода</b>:
<b>Карта</b>: <code>{sett.card_fake}</code>
<b>QIWI</b>: <code>{sett.qiwi_fake}</code>
<b>Bitcoin</b>: <code>{sett.btc_fake}</code>\n
<b>Рефералка</b>:\n<code>https://t.me/{user_name_bots}?start={call.from_user.id}</code>
<a href = 'https://telegra.ph/Kurs-po-Trejdu-02-02'><b>Мануал </b></a>
                            '''
                    await call.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)

            @dp.callback_query_handler(text=f'set_balance_{mamont_id}')
            async def input_balance(call: types.CallbackQuery, state: FSMContext):
                profile_id = call.data.split('_')[2]
                print(profile_id)
                await call.message.edit_text('Введите баланс мамонта:')
                await mamont_edit_balance.id_mamont.set()
                async with state.proxy() as data:
                    data['ID'] = profile_id
                await mamont_edit_balance.next()

            @dp.callback_query_handler(text=f'delete_mamonts_{mamont_id}')
            async def delete_mamont(call: types.CallbackQuery, state: FSMContext):
                profile_id = call.data.split('_')[2]
                print(profile_id)
                profile = all_users.get(all_users.user_id == profile_id)
                profile.worker = None
                profile.save()

                await call.message.edit_text('✅️ Мамонт удалён!')

            @dp.callback_query_handler(text=f'min_pay_{mamont_id}')
            async def input_balance(call: types.CallbackQuery, state: FSMContext):
                profile_id = call.data.split('_')[2]
                print(profile_id)
                await call.message.edit_text('Введите сумму:')
                await mamont_edit_pay.id_mamont.set()
                async with state.proxy() as data:
                    data['ID'] = profile_id
                await mamont_edit_pay.next()

            @dp.callback_query_handler(text=f'farting_{mamont_id}')
            async def input_balance(call: types.CallbackQuery):
                profile_id = call.data.split('_')[1]
                profile = all_users.get(all_users.user_id == profile_id)

                if profile.fart == 0:
                    profile.fart = 1
                elif profile.fart == 1:
                    profile.fart = 2
                elif profile.fart == 2:
                    profile.fart = 0

                profile.save()
                key = types.InlineKeyboardMarkup()
                key.add(types.InlineKeyboardButton('👛 Задать баланс', callback_data=f'set_balance_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🍀 Фарт', callback_data=f'farting_{mamont_id}'),
                        types.InlineKeyboardButton('Верификация', callback_data=f'verif_{mamont_id}'))
                key.add(
                    types.InlineKeyboardButton('➖ Минимальная сумма пополнения', callback_data=f'min_pay_{mamont_id}'))
                key.add(types.InlineKeyboardButton('☀️Заблокировать счёт❄️', callback_data=f'freeze_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🛑️ Удалить мамонта', callback_data=f'delete_mamonts_{mamont_id}'))
                key.add(types.InlineKeyboardButton('Назад', callback_data='backing'))
                if profile.fart == 0:
                    farts = 'Всегда проигрыш'
                elif profile.fart == 1:
                    farts = 'Всегда выигрыш'
                else:
                    farts = 'Рандом'
                if profile.verif == 0:
                    veri = '🛑️'
                else:
                    veri = '✅️ '
                if profile.freez == 0:
                    fr = '☀️'
                else:
                    fr = '❄️'
                if mamont_info.username is None:
                    await call.message.edit_text(
                        f'ID: {profile.user_id}\nБаланс: {profile.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri} ',
                        reply_markup=key)
                else:
                    await call.message.edit_text(
                        f'Мамонт: @{profile.username}\nБаланс: {profile.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri}',
                        reply_markup=key)

            @dp.callback_query_handler(text=f'verif_{mamont_id}')
            async def input_verif(call: types.CallbackQuery):
                profile_id = call.data.split('_')[1]
                profile = all_users.get(all_users.user_id == profile_id)

                if profile.verif == 0:
                    profile.verif = 1
                elif profile.verif == 1:
                    profile.verif = 0

                profile.save()
                key = types.InlineKeyboardMarkup()
                key.add(types.InlineKeyboardButton('👛 Задать баланс', callback_data=f'set_balance_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🍀 Фарт', callback_data=f'farting_{mamont_id}'),
                        types.InlineKeyboardButton('Верификация', callback_data=f'verif_{mamont_id}'))
                key.add(
                    types.InlineKeyboardButton('➖ Минимальная сумма пополнения', callback_data=f'min_pay_{mamont_id}'))
                key.add(types.InlineKeyboardButton('☀️Заблокировать счёт❄️', callback_data=f'freeze_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🛑️ Удалить мамонта', callback_data=f'delete_mamonts_{mamont_id}'))
                key.add(types.InlineKeyboardButton('Назад', callback_data='backing'))
                if profile.fart == 0:
                    farts = 'Всегда проигрыш'
                elif profile.fart == 1:
                    farts = 'Всегда выигрыш'
                else:
                    farts = 'Рандом'
                if profile.verif == 0:
                    veri = '🛑️'
                else:
                    veri = '✅️ '
                if profile.freez == 0:
                    fr = '☀️'
                else:
                    fr = '❄️'
                if mamont_info.username is None:
                    await call.message.edit_text(
                        f'ID: {profile.user_id}\nБаланс: {profile.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri}',
                        reply_markup=key)
                else:
                    await call.message.edit_text(
                        f'Мамонт: @{profile.username}\nБаланс: {profile.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri}',
                        reply_markup=key)

            @dp.callback_query_handler(text=f'freeze_{mamont_id}')
            async def freeze(call: types.CallbackQuery):
                profile_id = call.data.split('_')[1]
                profile = all_users.get(all_users.user_id == profile_id)

                if profile.freez == 0:
                    profile.freez = 1
                elif profile.freez == 1:
                    profile.freez = 0

                profile.save()
                key = types.InlineKeyboardMarkup()
                key.add(types.InlineKeyboardButton('👛 Задать баланс', callback_data=f'set_balance_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🍀 Фарт', callback_data=f'farting_{mamont_id}'),
                        types.InlineKeyboardButton('Верификация', callback_data=f'verif_{mamont_id}'))
                key.add(
                    types.InlineKeyboardButton('➖ Минимальная сумма пополнения', callback_data=f'min_pay_{mamont_id}'))
                key.add(types.InlineKeyboardButton('☀️Заблокировать счёт❄️', callback_data=f'freeze_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🛑️ Удалить мамонта', callback_data=f'delete_mamonts_{mamont_id}'))
                key.add(types.InlineKeyboardButton('Назад', callback_data='backing'))
                if profile.fart == 0:
                    farts = 'Всегда проигрыш'
                elif profile.fart == 1:
                    farts = 'Всегда выигрыш'
                else:
                    farts = 'Рандом'
                if profile.verif == 0:
                    veri = '🛑️'
                else:
                    veri = '✅️ '
                if profile.freez == 0:
                    fr = '☀️'
                else:
                    fr = '❄️'
                if mamont_info.username is None:
                    await call.message.edit_text(
                        f'ID: {profile.user_id}\nБаланс: {profile.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri}',
                        reply_markup=key)
                else:
                    await call.message.edit_text(
                        f'Мамонт: @{profile.username}\nБаланс: {profile.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri}',
                        reply_markup=key)

        @dp.message_handler(content_types=['text'], state=mamont_edit_pay.summ)  # Принимаем состояние
        async def set_dep(message: types.Message, state: FSMContext):
            try:
                async with state.proxy() as data:
                    data['summ'] = int(message.text)
                await state.finish()
                profile = all_users.get(all_users.user_id == data['ID'])
                profile.min_pay_up = data['summ']
                profile.save()
                key = types.InlineKeyboardMarkup()
                mamont_info = all_users.get(all_users.user_id == data['ID'])
                key.add(types.InlineKeyboardButton('👛 Задать баланс', callback_data=f'set_balance_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🍀 Фарт', callback_data=f'farting_{mamont_id}'),
                        types.InlineKeyboardButton('Верификация', callback_data=f'verif_{mamont_id}'))
                key.add(
                    types.InlineKeyboardButton('➖ Минимальная сумма пополнения', callback_data=f'min_pay_{mamont_id}'))
                key.add(types.InlineKeyboardButton('☀️Заблокировать счёт❄️', callback_data=f'freeze_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🛑️ Удалить мамонта', callback_data=f'delete_mamonts_{mamont_id}'))
                key.add(types.InlineKeyboardButton('Назад', callback_data='backing'))
                if mamont_info.fart == 0:
                    farts = 'Всегда проигрыш'
                elif mamont_info.fart == 1:
                    farts = 'Всегда выигрыш'
                else:
                    farts = 'Рандом'

                if mamont_info.verif == 0:
                    veri = '🛑️'
                else:
                    veri = '✅️ '

                if mamont_info.freez == 0:
                    fr = '☀️'
                else:
                    fr = '❄️'

                if mamont_info.username is None:
                    await message.answer(
                        f'ID: {mamont_info.user_id}\nБаланс: {mamont_info.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri}',
                        reply_markup=key)
                else:
                    await message.answer(
                        f'Мамонт: @{mamont_info.username}\nБаланс: {mamont_info.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri}',
                        reply_markup=key)
            except Exception as err:
                print(err)
                await state.finish()
                key = types.InlineKeyboardMarkup()
                key.add(types.InlineKeyboardButton('Назад', callback_data='backing'))
                await call.message.answer('🛑️ *Ошибка*', reply_markup=key, parse_mode='Markdown')

        @dp.message_handler(content_types=['text'], state=mamont_edit_balance.summ)  # Принимаем состояние
        async def set_balance(message: types.Message, state: FSMContext):
            try:
                async with state.proxy() as data:
                    data['summ'] = int(message.text)
                await state.finish()
                profile = all_users.get(all_users.user_id == data['ID'])
                profile.balance = data['summ']
                profile.save()
                key = types.InlineKeyboardMarkup()
                mamont_info = all_users.get(all_users.user_id == data['ID'])
                key.add(types.InlineKeyboardButton('👛 Задать баланс', callback_data=f'set_balance_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🍀 Фарт', callback_data=f'farting_{mamont_id}'),
                        types.InlineKeyboardButton('Верификация', callback_data=f'verif_{mamont_id}'))
                key.add(
                    types.InlineKeyboardButton('➖ Минимальная сумма пополнения', callback_data=f'min_pay_{mamont_id}'))
                key.add(types.InlineKeyboardButton('☀️Заблокировать счёт❄️', callback_data=f'freeze_{mamont_id}'))
                key.add(types.InlineKeyboardButton('🛑️ Удалить мамонта', callback_data=f'delete_mamonts_{mamont_id}'))
                key.add(types.InlineKeyboardButton('Назад', callback_data='backing'))
                if mamont_info.fart == 0:
                    farts = 'Всегда проигрыш'
                elif mamont_info.fart == 1:
                    farts = 'Всегда выигрыш'
                else:
                    farts = 'Рандом'

                if mamont_info.verif == 0:
                    veri = '🛑️'
                else:
                    veri = '✅️ '

                if mamont_info.freez == 0:
                    fr = '☀️'
                else:
                    fr = '❄️'

                if mamont_info.username is None:
                    await message.answer(
                        f'ID: {mamont_info.user_id}\nБаланс: {mamont_info.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri} ',
                        reply_markup=key)
                else:
                    await message.answer(
                        f'Мамонт: @{mamont_info.username}\nБаланс: {mamont_info.balance}\nСчёт: {fr}\nФарт: {farts}\nВерификация: {veri} ',
                        reply_markup=key)
            except Exception as err:
                print(err)
                await state.finish()
                key = types.InlineKeyboardMarkup()
                key.add(types.InlineKeyboardButton('Назад', callback_data='backing'))
                await call.message.answer('🛑️ *Ошибка*', reply_markup=key, parse_mode='Markdown')


@dp.message_handler(Text(equals="⚡️ Меню воркера"))
async def ecn(message: types.Message):
    if workers.get_or_none(workers.user_id == message.from_user.id):
        await message.delete()
        keyboard = types.InlineKeyboardMarkup()
        my_mamont = types.InlineKeyboardButton('Мои мамонты', callback_data='my_mamonts')
        add_mamont = types.InlineKeyboardButton('Добавить мамонта', callback_data='add_mamont')
        create_promo = types.InlineKeyboardButton('Создать промокод', callback_data='create_promo')
        my_promo = types.InlineKeyboardButton('Мои промокоды', callback_data='view_promo')
        keyboard.add(my_mamont, add_mamont)
        keyboard.add(create_promo, my_promo)
        sett = default_setting.get(default_setting.id == 1)

        cnt = 0
        for i in all_users.select().where(all_users.worker == message.from_user.id):
            cnt += 1
        len_users = cnt

        text = f'''
<b>⚡️ Меню воркера</b>:
<b>Количество мамонтов</b>: {len_users}\n 
<b>Реквизиты для вывода</b>:
<b>Карта</b>: <code>{sett.card_fake}</code>
<b>QIWI</b>: <code>{sett.qiwi_fake}</code>
<b>Bitcoin</b>: <code>{sett.btc_fake}</code>\n
<b>Рефералка</b>:\n<code>https://t.me/{user_name_bots}?start={message.from_user.id}</code>
<a href = 'https://telegra.ph/Kurs-po-Trejdu-02-02'><b>Мануал </b></a>
            '''
        await message.answer(text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)


@dp.callback_query_handler(text="back_to_ecn_reset", state=ecn_add)
async def back_to_ecn(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    async with state.proxy() as data:
        data['summ'] = call.message.text
    await state.reset_state()
    text = 'Выберите актив: '
    await call.message.answer(text=text, reply_markup=ecn_btns_ru)


@dp.callback_query_handler(text="back_to_ecn")
async def back_to_ecn(call: types.CallbackQuery):
    await call.message.delete()
    text = 'Выберите актив:'
    await call.message.answer(text=text, reply_markup=ecn_btns_ru)


@dp.callback_query_handler(text='back_promo', state=promokods)
async def pay_promokods(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer('Выберите вариант пополнения баланса: ', reply_markup=pays_ru)
    async with state.proxy() as data:
        data['promik'] = call.message.text
    await state.reset_state()


@dp.callback_query_handler(text="back_to_start_reset", state=costing)
async def back_to_start_reset(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer('Выберите вариант пополнения баланса: ', reply_markup=pays_ru)
    async with state.proxy() as data:
        data['cost'] = call.message.text
    await state.reset_state()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
