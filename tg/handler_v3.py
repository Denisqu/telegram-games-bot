import telebot
import re
from telebot import types
import random
from core.game import GameSession
import json
import yaml
import random

begin_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
begin_keyboard.row('Начать игру за X', 'Начать игру за O')

restart_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
restart_keyboard.row('Замечательная партия! Продолжим игру.')

bot = telebot.TeleBot("6596300742:AAHZkLqBwk3qWdqzkBS5UJiUunogzRLcmnI")

good_jokes_json = None
bad_jokes_json = None
with open('./resources/goodjokes.json', encoding="utf8") as f:
    #good_jokes_json = yaml.safe_load(f)
    good_jokes_json = json.load(f)
with open('./resources/badjokes.json', encoding="utf8") as f:
    #bad_jokes_json = yaml.safe_load(f)
    bad_jokes_json = json.load(f)


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
    session.seen_good_jokes_ids_list = []
    session.seen_bad_jokes_ids_list = []
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
            session.user_figure = 'X'
            session.AI_figure = 'O'
            reply_text = 'Играем за X. \nВыберете нужную позицию для вашего хода'
    
    begin_field_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    session.begin_field_keyboard = begin_field_keyboard
    for row in session.field_repr:
        # трансформируем поле в кнопки телеграмма
        begin_field_keyboard.row(row[0], row[1], row[2])
    bot.send_message(message.chat.id, reply_text, reply_markup=begin_field_keyboard)
    bot.register_next_step_handler(message, next_message_reply, session)

def next_message_reply(message, session=None):
    # player logical move
    is_valid_parsed, row, column = parse_step_input(message.text)
    is_valid_move = session.user_step((row, column))
    if not (is_valid_move or is_valid_parsed):
        bot.send_message(message.chat.id, "Неправильный ход, попробуй ещё раз", reply_markup=session.begin_field_keyboard)
        bot.register_next_step_handler(message, next_message_reply, session)
        return
    # render player move
    session.field_repr[row][column] = session.user_figure

    session.print_current_state()

    # check for player win
    if session.wins(session.game_state, session.HUMAN):
        bot.send_message(message.chat.id, f"Вы победили! Ваш анекдот: \n {get_good_anecdote(session)}", reply_markup=restart_keyboard)
        bot.register_next_step_handler(message, start, session)
        return
    # check for draw
    if len(session.empty_cells()) == 0:
        bot.send_message(message.chat.id, f"Ничья! Ваш анекдот: \n {get_good_anecdote(session)}", reply_markup=restart_keyboard)
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
        bot.send_message(message.chat.id, f"Ничья! Ваш анекдот: \n {get_good_anecdote(session)}", reply_markup=restart_keyboard)
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
        return (True, user_coords[0], user_coords[1])
    return False, None, None
    
def get_good_anecdote(session):
    if len(session.seen_good_jokes_ids_list) >= len(good_jokes_json):
        session.seen_good_jokes_ids_list = []
    i, anecdote = 0, None
    while True:
        i += 1
        anecdote = good_jokes_json[random.randrange(0, len(good_jokes_json))]
        if anecdote["id"] not in session.seen_good_jokes_ids_list:
            session.seen_good_jokes_ids_list.append(anecdote["id"])
            return anecdote["joke"]
        if i >= 10:
            return anecdote["joke"]

    

def get_bad_anecdote(session):
    if len(session.seen_good_jokes_ids_list) >= len(bad_jokes_json):
        session.seen_bad_jokes_ids_list = []
    i, anecdote = 0, None
    while True:
        i += 1
        anecdote = bad_jokes_json[random.randrange(0, len(bad_jokes_json))]
        if anecdote["id"] not in session.seen_bad_jokes_ids_list:
            session.seen_bad_jokes_ids_list.append(anecdote["id"])
            return anecdote["joke"]
        if i >= 10:
            return anecdote["joke"]
    
if __name__ == '__main__':
    bot.polling(none_stop=True)