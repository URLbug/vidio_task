from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from unidecode import unidecode

import json
import datetime

from database import session, User
from context import Balans


config = json.load(open('config.json', 'rb'))

bot = Bot(config['TOKEN'])
dp = Dispatcher(bot, storage=MemoryStorage())

price = {'price': 20}
msg = {'message': None}

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(
        types.KeyboardButton('📷 Уникализация'),
        types.KeyboardButton('👤 Профиль'),
        types.KeyboardButton('🆘 Тех. поддержка'),
        types.KeyboardButton('📕 Правила'),
    )

    if m.from_user.id not in [i.user_id for i in session.query(User.user_id).distinct()]:
        user = User(
            username=unidecode(m.from_user.full_name), 
            user_id=m.from_user.id, 
            balans=0, 
            regis=str(datetime.datetime.now()),
            uniqueized=0,
            comand='Отсутствует'
            )

        session.add(user)
        session.commit()
        session.close()

    await m.reply("""
    Привет, приступим к уникализации или накрутке?

Обязательно ознакомтесь с правилами: https://telegra.ph/Pravila-TrafUniqueBot-10-18
    """, reply_markup=build)

@dp.message_handler(text='📷 Уникализация')
async def uniqueized(m: types.Message):
    
    balans = [[i.balans] for i in session.query(User).filter_by(username=m.from_user.full_name)][0][0]

    if balans < price['price']:

        await m.reply(f'''На вашем балансе недостаточно средств.
        Минимальная стоимость - {price['price']}₽''')
    else:
        await m.reply('goal')

@dp.message_handler(text='👤 Профиль', state=None)
async def profil(m: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('💰 Пополнить баланс', callback_data='balans_pluse'),
        types.InlineKeyboardButton('🎟Ввести промокод', callback_data='promocode')
    )
    
    user = [{
        'username': i.username, 
        'user_id': i.user_id, 
        'balans': i.balans,
        'regis': i.regis,
        'uniqueized': i.uniqueized,
        'comand': i.comand} for i in session.query(User).filter_by(username=m.from_user.full_name)][0]

    await m.reply(f'''
    🔑 Профиль
    
    
    Ваш ID: {user['user_id']}
    Баланс: {user['balans']}
    Регистрация: {user['regis']}
    Уникализировано: {user['uniqueized']}
    Команда: {user['comand']}''', reply_markup=markup)

    await state.finish()

@dp.callback_query_handler(text='balans_pluse', state=None)
async def balans_pluse(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('↪️Назад', callback_data='profil_false' )
    )

    msg['message'] = await call.message.edit_text(
        'Введите сумму, на которую хотите пополнить баланс', reply_markup=markup)
    

    await Balans.balans.set()

@dp.callback_query_handler(text='profil_false', state=Balans.balans)
async def profil_false(call: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('💰 Пополнить баланс', callback_data='balans_pluse'),
        types.InlineKeyboardButton('🎟Ввести промокод', callback_data='promocode')
    )
    
    user = [{
        'username': i.username, 
        'user_id': i.user_id, 
        'balans': i.balans,
        'regis': i.regis,
        'uniqueized': i.uniqueized,
        'comand': i.comand} for i in session.query(User).filter_by(username=call.from_user.full_name)][0]

    await call.message.edit_text(f'''
    🔑 Профиль
    
    
    Ваш ID: {user['user_id']}
    Баланс: {user['balans']}
    Регистрация: {user['regis']}
    Уникализировано: {user['uniqueized']}
    Команда: {user['comand']}''', reply_markup=markup)

    await state.finish()

@dp.message_handler(state=Balans.balans)
async def balans_pluse_2(m: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('☑️Проверить оплату', callback_data='sea_balans'),
        types.InlineKeyboardButton('💳Перейти к оплате', url='https://zelenka.guru/'),
        types.InlineKeyboardButton('🚫Отменить платеж', callback_data='del_balans'),    
    )

    text = m.text
    today = str(datetime.datetime.today())

    await msg['message'].delete()

    msg['message'] = await m.reply(
        f'''
        💴Пополнение баланса
        ├👤Ваш ID: {m.from_user.id}
        ├💰Сумма пополнения: {text}₽
        ├✔️Способ оплаты: LolzTeam Market 💲
        ├🗓Сегодняшняя дата: {today}
        ├🕟Время на оплату чека: Не ограничено
        └💬Комментарий к переводу (обязательно): zcSUS
        ''', reply_markup=markup)
    
    await bot.delete_message(chat_id=m.from_user.id, message_id=m.message_id)
    
    await state.finish() 

@dp.callback_query_handler(text='del_balans')
async def del_balans(m: types.Message):
    await msg['message'].delete()


@dp.message_handler(text='🆘 Тех. поддержка')
async def supports(m: types.Message):
    await m.reply(
        'Если у вас возникли какие-либо вопросы - вы можете обратиться к саппорту'
    )

@dp.message_handler(text='📕 Правила')
async def supports(m: types.Message):
    await m.reply(
        'Актуальные правила можно прочитать здесь:\nhttps://telegra.ph/Pravila-TrafUniqueBot-10-18'
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)