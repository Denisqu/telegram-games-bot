import telebot
import re
from telebot import types

bot = telebot.TeleBot("Put your token")

#   ПРИМЕР
#
#   Приветствие
#   -> Начать игру за X; -> Начать игру за O
#   Вывод поля игры:
#   ->|(1,3)|       ->|(2,3)|       ->|(3,3)|
#   ->|(1,2)|       ->|(2,2)|       ->|(3,2)|
#   ->|(1,1)|       ->|(2,1)|       ->|(3,1)|
#   Вывод поля игры после хода бота:
#   ->|X|           ->|(2,3)|       ->|(3,3)|
#   ->|O|           ->|(2,2)|       ->|(3,2)|
#   ->|(1,1)|       ->|(2,1)|       ->|(3,1)|
#   Вывод поля игры после хода бота:
#   ->|X|           ->|(2,3)|       ->|(3,3)|
#   ->|O|           ->|X|           ->|(3,2)|
#   ->|O|           ->|(2,1)|       ->|(3,1)|
#   Вывод поля игры без хода бота, если Пользователь победил:
#   ->|X|           ->|(2,3)|       ->|(3,3)|
#   ->|O|           ->|X|           ->|(3,2)|
#   ->|O|           ->|(2,1)|       ->|X|
#   Вывод, что Пользователь победил и молодец
#   Вывод хорошего анекдота
#   Вывод не хочет ли Пользователь начать новую игру
#   -> Начать игру за X; -> Начать игру за O

user_figure = None
AI_figure = None
field = ['(1,3)', '(2,3)', '(3,3)',
         '(1,2)', '(2,2)', '(3,2)',
         '(1,1)', '(2,1)', '(3,1)']

begin_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
begin_keyboard.row('Начать игру за X', 'Начать игру за O')

begin_field_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
for i in range(0, 9, 3):
    begin_field_keyboard.row(field[i], field[i+1], field[i+2])


@bot.message_handler(commands=['start'])
def start(message):
    start_message = "Приветствие"
    bot.send_message(message.chat.id, start_message, reply_markup=begin_keyboard)


@bot.message_handler(content_types=['text'])
def next_message_reply(message):
    global user_figure, AI_figure, field

    if message.text == "Начать игру за X":
        user_figure = 'X'
        AI_figure = 'O'
        text = 'Играем за X. \nВыберете нужную позицию для вашего хода'
        bot.send_message(message.chat.id, text,
                         reply_markup=begin_field_keyboard)

    if message.text == "Начать игру за O":
        user_figure = 'O'
        AI_figure = 'X'
        text = 'Играем за O. \nВыберете нужную позицию для вашего хода'
        bot.send_message(message.chat.id, text, reply_markup=begin_field_keyboard)

    if re.search(r'\([123],[123]\)', message.text):
        user_coords = message.text.split(',')
        user_coords[0] = int(user_coords[0].replace('(', ''))
        user_coords[1] = int(user_coords[1].replace(')', ''))
        update_field(user_coords, user_figure)

        AI_coords = tic_tac_toe_AI(user_coords, field)
        update_field(AI_coords, AI_figure)

        session_field_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        for i in range(0, 9, 3):
            session_field_keyboard.row(field[i], field[i + 1], field[i + 2])

        bot.send_message(message.chat.id, 'Вы сделали ход', reply_markup=session_field_keyboard)
        pass


def update_field(change_coords, figure):
    global field
    field_position = (change_coords[0] - 1) + 3 * (3 - change_coords[1])
    field[field_position] = figure


def tic_tac_toe_AI(move, current_field):
    """
    TODO: отправлять текущее состояние поля (?),
          в котором есть координаты, если данная клетка не заполнена
          и O или X, если на этой клетке соответствующая фигура
    TODO: логика игры

    :param move: картеж координат хода Пользователя
    :param current_field: текущее состояние поля
    :return: картеж координат хода ИИ
    """
    return 1, 3


bot.polling(none_stop=True)
