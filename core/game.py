from math import inf as infinity
from random import choice

class GameSession:
    def __init__(self):
        self.game_state = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        self.HUMAN = -1
        self.COMP = +1

    def user_step(self, position):
        '''
        Ход юзера
        '''
        x, y = position
        if self.valid_move(x, y):
            self.set_move(x, y, self.HUMAN)
            return True
        else:
            return False

    def bot_step(self):
        '''
        Ход бота
        '''
        depth = len(self.empty_cells())
        if depth == 0 or self.game_over():
            return

        move = self.minimax(self.game_state, depth, self.COMP)
        x, y = move[0], move[1]
        self.set_move(x, y, self.COMP)
        return x, y

    def print_current_state(self):
        '''
        Выводит текущее состояние игровой доски в консоль
        '''
        chars = {
            -1: 'X',
            +1: 'O',
            0: ' '
        }
        str_line = '---------------'

        print('\n' + str_line)
        for row in self.game_state:
            for cell in row:
                symbol = chars[cell]
                print(f'| {symbol} |', end='')
            print('\n' + str_line)

    def evaluate(self, state):
        '''
        Функция для эвристической оценки состояния.
        :param state: текущее состояние доски
        :return: +1, если выиграл компьютер; -1, если выиграл человек; 0 - ничья
        '''
        if self.wins(state, self.COMP):
            return +1
        elif self.wins(state, self.HUMAN):
            return -1
        else:
            return 0

    def wins(self, state, player):
        '''
        Проверяет, выиграл ли указанный игрок. Возможности:
        * Три ряда [X X X] или [O O O]
        * Три столбца [X X X] или [O O O]
        * Две диагонали [X X X] или [O O O]
        :param state: текущее состояние доски
        :param player: человек или компьютер
        :return: True, если игрок выиграл
        '''
        win_state = [
            [state[0][0], state[0][1], state[0][2]],
            [state[1][0], state[1][1], state[1][2]],
            [state[2][0], state[2][1], state[2][2]],
            [state[0][0], state[1][0], state[2][0]],
            [state[0][1], state[1][1], state[2][1]],
            [state[0][2], state[1][2], state[2][2]],
            [state[0][0], state[1][1], state[2][2]],
            [state[2][0], state[1][1], state[0][2]],
        ]
        return [player, player, player] in win_state

    def game_over(self):
        '''
        Проверяет, выиграл ли человек или компьютер
        :return: True, если выиграл человек или компьютер
        '''
        return self.wins(self.game_state, self.HUMAN) or self.wins(self.game_state, self.COMP)

    def empty_cells(self):
        '''
        Каждая пустая ячейка добавляется в список cells
        :return: список пустых ячеек
        '''
        cells = []
        for x, row in enumerate(self.game_state):
            for y, cell in enumerate(row):
                if cell == 0:
                    cells.append([x, y])
        return cells

    def valid_move(self, x, y):
        '''
        Ход допустим, если выбранная ячейка пуста
        :param x: координата X
        :param y: координата Y
        :return: True, если board[x][y] пуста
        '''
        if x is None or y is None:
            return False

        if [x, y] in self.empty_cells():
            return True
        else:
            return False

    def set_move(self, x, y, player):
        '''
        Устанавливает ход на доске, если координаты допустимы
        :param x: координата X
        :param y: координата Y
        :param player: текущий игрок
        '''
        if self.valid_move(x, y):
            self.game_state[x][y] = player

    def minimax(self, state, depth, player):
        '''
        AI функция, выбирающая лучший ход
        :param state: текущее состояние доски
        :param depth: индекс узла в дереве (0 <= depth <= 9),
        но никогда не 9 в этом случае (см. функцию ai_turn())
        :param player: человек или компьютер
        :return: список с [лучшей строкой, лучшим столбцом, лучшим счетом]
        '''
        if player == self.COMP:
            best = [-1, -1, -infinity]
        else:
            best = [-1, -1, +infinity]

        if depth == 0 or self.game_over():
            score = self.evaluate(state)
            return [-1, -1, score]

        for cell in self.empty_cells():
            x, y = cell[0], cell[1]
            state[x][y] = player
            score = self.minimax(state, depth - 1, -player)
            state[x][y] = 0
            score[0], score[1] = x, y

            if player == self.COMP:
                if score[2] > best[2]:
                    best = score  # максимальное значение
            else:
                if score[2] < best[2]:
                    best = score  # минимальное значение

        return best
    
if __name__ == '__main__':
    game_session = GameSession()

    while len(game_session.empty_cells()) > 0 and not game_session.game_over():
        # Ход пользователя
        print("Текущее состояние:")
        game_session.print_current_state()
        user_input = input("Введите свой ход (строка и столбец, разделённые пробелом): ")
        try:
            user_move = [int(coord) for coord in user_input.split()]
            if game_session.user_step(user_move):
                print("...")
            else:
                print("Некорректный ход. Попробуйте снова.")
                continue
        except (ValueError, IndexError):
            print("Неправильный ввод. Пожалуйста, введите две цифры, разделённые пробелом.")
            continue

        # Проверка завершения игры после хода пользователя
        if game_session.game_over():
            print("Игра окончена!")
            break
        elif len(game_session.empty_cells()) == 0:
            print("Ничья!")
            break

        # Ход бота
        print("Ход бота:")
        game_session.bot_step()

        # Проверка завершения игры после хода бота
        if game_session.game_over():
            print("Игра окончена!")
            break
        elif len(game_session.empty_cells()) == 0:
            print("Ничья!")
            break

    print("Результат:")
    game_session.print_current_state()