from aiogram import types

keyboard_accept_license = types.InlineKeyboardMarkup()
keyboard_accept_license.add(types.InlineKeyboardButton(text="✅ Согласен", callback_data="accept_licence"))


setting_ru = types.InlineKeyboardMarkup()
setting_ru.add(types.InlineKeyboardButton('Написать', url='https://t.me/royaldarktp'))
#setting_ru.add(types.InlineKeyboardButton('🇷🇺 Язык 🇺🇸', callback_data='language'))
setting_ru.add(types.InlineKeyboardButton('Назад', callback_data='back_to_start'))

settingback = types.InlineKeyboardMarkup()
settingback.add(types.InlineKeyboardButton('Назад', callback_data='back_to_start'))

ecn_btns_ru = types.InlineKeyboardMarkup(row_width=2)
ecn_btns_ru.add(types.InlineKeyboardButton(text='📈 Crash', callback_data="crash"),
                types.InlineKeyboardButton(text='🎲 КУБИК', callback_data="kubik"),
                types.InlineKeyboardButton(text='🎱 Рандомное число', callback_data="rnd_num"),
                types.InlineKeyboardButton(text='🤹‍♀️ Орел & Решка', callback_data="orel_reshka"))

pays_ru = types.InlineKeyboardMarkup()
pays_ru.add(types.InlineKeyboardButton('💳 Пополнить через карту или QIWI 🥝', callback_data='add_balance_pay'))
pays_ru.add(types.InlineKeyboardButton('🎁 Ввести промокод', callback_data='pay_promo'))

back_to_start_ru = types.InlineKeyboardMarkup()
back_to_start_ru.add(types.InlineKeyboardButton('Назад', callback_data='back_to_start'))

back_promo_ru = types.InlineKeyboardMarkup()
back_promo_ru.add(types.InlineKeyboardButton('Назад', callback_data='back_promo'))

back_to_start_reset_ru = types.InlineKeyboardMarkup()
back_to_start_reset_ru.add(types.InlineKeyboardButton('Назад', callback_data='back_to_start_reset'))