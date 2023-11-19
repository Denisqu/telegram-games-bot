import telebot
import re
from telebot import types
import random
from core.game import GameSession

begin_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
begin_keyboard.row('Начать игру за X', 'Начать игру за O')

restart_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
restart_keyboard.row('ГГ, ГО НЕКСТ')

bot = telebot.TeleBot("6596300742:AAEq0AK0_M94haOze6ogNxx57QzM2q_qqLw")

@bot.message_handler(commands=['start'])
def start(message, session=None):
    start_message = "Здравствуйте! Хотите сыграть в крестики-нолики?"
    
    # Вывод в консоль имени ползьзователя. Можно убрать.
    print(message.from_user.first_name)

    bot.send_message(message.chat.id, start_message, reply_markup=begin_keyboard)

    # отправляем пользователя с его сессией на следующий шаг
    session = GameSession()
    session.field_repr = [['(0,0)', '(0,1)', '(0,2)'],
             ['(1,0)', '(1,1)', '(1,2)'],
             ['(2,0)', '(2,1)', '(2,2)']]
    bot.register_next_step_handler(message, start_game_message_reply, session)

def start_game_message_reply(message, session=None):
    reply_text = None
    match message.text:
        case "Начать игру за X":
            session.user_figure = 'X'
            session.AI_figure = 'O'
            reply_text = 'Играем за X. \nВыберете нужную позицию для вашего хода'
        case "Начать игру за O":
            session.user_figure = 'O'
            session.AI_figure = 'X'
            reply_text = 'Играем за O. \nВыберете нужную позицию для вашего хода'
        case _:
            print(f'Wrong message in start_game_message_reply: message = {message.text}')
    
    begin_field_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    session.begin_field_keyboard = begin_field_keyboard
    for row in session.field_repr:
        # трансформируем поле в кнопки телеграмма
        begin_field_keyboard.row(row[0], row[1], row[2])
    bot.send_message(message.chat.id, reply_text, reply_markup=begin_field_keyboard)
    bot.register_next_step_handler(message, next_message_reply, session)

def next_message_reply(message, session=None):
    # player logical move
    row, column = parse_step_input(message.text)
    is_valid_move = session.user_step((row, column))
    if not is_valid_move:
        bot.send_message(message.chat.id, "Неправильный ход, попробуй ещё раз", reply_markup=session.begin_field_keyboard)
        bot.register_next_step_handler(message, next_message_reply, session)
        return
    # render player move
    session.field_repr[row][column] = session.user_figure

    session.print_current_state()

    # check for player win
    if session.wins(session.game_state, session.HUMAN):
        bot.send_message(message.chat.id, f"Вы победили! Ваш анекдот: \n {get_good_anecdote(session)}", reply_markup=session.restart_keyboard)
        bot.register_next_step_handler(message, start, session)
        return
    # check for draw
    if len(session.empty_cells()) == 0:
        bot.send_message(message.chat.id, f"Ничья! Ваш анекдот: \n {get_good_anecdote(session)}", reply_markup=session.restart_keyboard)
        bot.register_next_step_handler(message, start, session)
        return
    
    # AI logical move
    row, column = session.bot_step()
    
    session.print_current_state()

    # render AI move
    session.field_repr[row][column] = session.AI_figure
    # synch keyboard with field_repr
    session.begin_field_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    for row in session.field_repr:
        # трансформируем поле в кнопки телеграмма
        session.begin_field_keyboard.row(row[0], row[1], row[2])

    # check for AI win
    if session.wins(session.game_state, session.COMP):
        bot.send_message(message.chat.id, f"Вы проиграли! Ваш анекдот: \n {get_bad_anecdote(session)}", reply_markup=restart_keyboard)
        bot.register_next_step_handler(message, start, session)
        return
    
    # check for draw
    if len(session.empty_cells()) == 0:
        bot.send_message(message.chat.id, f"Ничья! Ваш анекдот: \n {get_good_anecdote(session)}", reply_markup=session.restart_keyboard)
        bot.register_next_step_handler(message, start, session)
        return
    
    bot.send_message(message.chat.id, "...", reply_markup=session.begin_field_keyboard)
    bot.register_next_step_handler(message, next_message_reply, session)

def parse_step_input(text):
    if re.search(r'\([012],[012]\)', text):
        # ход Пользователя
        user_coords = text.split(',')
        user_coords[0] = int(user_coords[0].replace('(', ''))
        user_coords[1] = int(user_coords[1].replace(')', ''))
        return (user_coords[0], user_coords[1])
    
def get_good_anecdote(session):
    return """Идут два арабских террориста-камикадзе на задание. anekdotov.net, Один — другому: \n
— Волнуешься? \n
Второй: \n
— А то? Первый раз все-таки!"""

def get_bad_anecdote(session):
    return """Что утром на двух ногах, днем на четырех, а вечером вновь на двух? \n
Рядовой Табуретка
"""
    
if __name__ == '__main__':
    bot.polling(none_stop=True)