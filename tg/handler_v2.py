import telebot
import re
from telebot import types
import random

bot = telebot.TeleBot("")

@bot.message_handler(commands=['start'])
def start(message):
    # Здесь создается сессия для пользоавтеля

    start_message = "Здравствуйте! Хотите сыграть в крестики-нолики?"
    field = ['(1,3)', '(2,3)', '(3,3)',
             '(1,2)', '(2,2)', '(3,2)',
             '(1,1)', '(2,1)', '(3,1)']

    # Вывод в консоль имени ползьзователя. Можно убрать.
    print(message.from_user.first_name)

    begin_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    begin_keyboard.row('Начать игру за X', 'Начать игру за O')
    bot.send_message(message.chat.id, start_message, reply_markup=begin_keyboard)

    # отправляем пользователя с его сессией на следующий шаг
    bot.register_next_step_handler(message, next_message_reply, field)

def next_message_reply(message, field=None, user_figure = 'X', AI_figure = 'O'):
    if message.text == "Начать игру за X":
        user_figure = 'X'
        AI_figure = 'O'
        text = 'Играем за X. \nВыберете нужную позицию для вашего хода'

        begin_field_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        for i in range(0, 9, 3):
            # трансформируем поле в кнопки телеграмма
            begin_field_keyboard.row(field[i], field[i + 1], field[i + 2])

        bot.send_message(message.chat.id, text, reply_markup=begin_field_keyboard)
        bot.register_next_step_handler(message, next_message_reply, field, user_figure, AI_figure)

    if message.text == "Начать игру за O":
        user_figure = 'O'
        AI_figure = 'X'
        text = 'Играем за O. \nВыберете нужную позицию для вашего хода'

        begin_field_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        for i in range(0, 9, 3):
            # трансформируем поле в кнопки телеграмма
            begin_field_keyboard.row(field[i], field[i + 1], field[i + 2])

        bot.send_message(message.chat.id, text, reply_markup=begin_field_keyboard)
        bot.register_next_step_handler(message, next_message_reply, field, user_figure, AI_figure)

    if re.search(r'\([123],[123]\)', message.text):
        # ход Пользователя
        user_coords = message.text.split(',')
        user_coords[0] = int(user_coords[0].replace('(', ''))
        user_coords[1] = int(user_coords[1].replace(')', ''))
        update_field(user_coords, user_figure, field)

        if did_anyone_win(user_figure, field):
            win_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
            win_keyboard.row('Увидеть крутой анекдот')
            bot.send_message(message.chat.id, 'Поздравляю! Вы победили! Теперь вам доступен крутой анекдот',
                             reply_markup=win_keyboard)
            bot.register_next_step_handler(message, next_message_reply, field)
            # TODO: тут иногда возникает проблема, когда пользователь отправляет сообщения быстрее, чем
            #       бот успевает отвечать. Пока что костыль - отправлять в следующий этап поле
            return

        # Ход ИИ
        AI_coords = tic_tac_toe_AI(user_coords, field, AI_figure, user_figure)
        update_field(AI_coords, AI_figure, field)
        if did_anyone_win(AI_figure, field):
            lose_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
            lose_keyboard.row('Увидеть унылый анекдот')
            bot.send_message(message.chat.id, 'К сожалению вы проиграли. Теперь вам доступен унылый анекдот',
                             reply_markup=lose_keyboard)
            bot.register_next_step_handler(message, next_message_reply)
            return

        # Проверка на ничью
        if is_draw(field, user_figure, AI_figure):
            draw_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
            draw_keyboard.row('/start')
            bot.send_message(message.chat.id, 'Ничья. Значит остаемся без анекдотов.\n\n'
                                              'Хотите сыграть еще?',
                             reply_markup=draw_keyboard)
            return

        session_field_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        for i in range(0, 9, 3):
            # трансформируем поле в кнопки телеграмма
            session_field_keyboard.row(field[i], field[i + 1], field[i + 2])

        bot.send_message(message.chat.id, 'Вы сделали ход', reply_markup=session_field_keyboard)
        bot.register_next_step_handler(message, next_message_reply, field, user_figure, AI_figure)

    if message.text == 'X' or message.text =='O':
        session_field_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        for i in range(0, 9, 3):
            # трансформируем поле в кнопки телеграмма
            session_field_keyboard.row(field[i], field[i + 1], field[i + 2])
        bot.send_message(message.chat.id, 'Нельзя ходить на уже занятую клетку!',
                         reply_markup=session_field_keyboard)
        bot.register_next_step_handler(message, next_message_reply, field, user_figure, AI_figure)

    if message.text == 'Увидеть унылый анекдот':
        start_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        start_keyboard.row('/start')
        # TODO: связать с базой плохих анекдотов
        bad_joke = ("- Сарочка, вы ничего не замечаете?\n"
                    "- Нет, ничего Розочка.\n"
                    "- Как, совсем ничего?\n"
                    "- Совсем.\n"
                    "- Я была в салоне красоты.\n"
                    "- Понятно")
        replay_text = '\n\nЕсли хотите еще раз сыграть, нажмите /start'
        bot.send_message(message.chat.id, bad_joke+replay_text, reply_markup=start_keyboard)

    if message.text == 'Увидеть крутой анекдот':
        start_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        start_keyboard.row('/start')
        # TODO: связать с базой хороших анекдотов
        good_joke = ("- Здесь\n"
                    "- должен быть очень смешной\n"
                    "- анекдот\n"
                    "- но я\n"
                    "- пока таких\n"
                    "- не нашел")
        replay_text = '\n\nЕсли хотите еще раз сыграть, нажмите /start'
        bot.send_message(message.chat.id, good_joke+replay_text, reply_markup=start_keyboard)

@bot.message_handler(content_types=['text'])
def unknown_command(message):
    unknown_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    unknown_keyboard.row('/start')
    bot.send_message(message.chat.id, 'Ваша команда \''+message.text+'\' не распознана.\n'
                                      'Сначала нажмите на /start, чтобы начать новую игру',
                     reply_markup=unknown_keyboard)

def update_field(change_coords, figure, field):
    """
    Ставит фигуру (X,O) на нужную координату на поле.

    :param change_coords: координата поля, где нужно поставить X/O
    :param figure: фигура X/O
    :param field: поле, где мы ставим X/O
    :return True - операция выполнена успешно
    """
    field_position = (change_coords[0] - 1) + 3 * (3 - change_coords[1])
    if field[field_position] == 'X' or field[field_position] == 'O':
        return False
    field[field_position] = figure
    return True

def did_anyone_win(figure, field):
    """
    Определяет выиграл ли уже кто-нибудь (пользователь/бот)

    :param figure: X/O
    :param field: текущее поле игры
    :return: True - победа была, False - победы не было
    """
    if field[0] == figure and field[4] == figure and field[8] == figure:
        # победа по диагонали \
        return True
    elif field[2] == figure and field[4] == figure and field[6] == figure:
        # победа по диагонали /
        return True

    for i in range(0,9,3):
        if field[i] == figure and field[i+1] == figure and field[i+2] == figure:
            # победа по горизонтали ---
            return True
    for i in range(0,3):
        if field[i] == figure and field[i+3] == figure and field[i+6] == figure:
            # победа по вертикали |
            return True
    return False

def is_draw(field, user_figure, AI_figure):
    """
    Проверяем получили ли ничью

    :param field: текущее игровое поле
    :param user_figure: X/O игрока
    :param AI_figure: X/O ИИ
    :return: True - ничья, False - продолжаем играть
    """
    for i in range(3):
        for j in range(3):
            if field[i + 3 * j] != user_figure and field[i + 3 * j] != AI_figure:
                return False
    return True


def tic_tac_toe_AI(move, current_field, AI_figure, user_figure):
    """
    TODO: отправлять текущее состояние поля (?),
          в котором есть координаты, если данная клетка не заполнена
          и O или X, если на этой клетке соответствующая фигура
    TODO: логика игры

    :param move: картеж координат хода Пользователя
    :param current_field: текущее состояние поля
    :return: картеж координат хода ИИ (какую кнопку заменить)
    """
    x = 1
    y = 1
    for j in range(0,3):
        for i in range(0,3):
            if current_field[j + i * 3] != AI_figure and current_field[j + i * 3] != user_figure:
                x = j + 1
                y = 3 - i
                break
    #y = random.randint(1, 3)
    return x, y

if __name__ == '__main__':
    bot.polling(none_stop=True)

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


