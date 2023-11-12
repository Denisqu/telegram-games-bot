

class GameSession:
    def __init__(self):
        self.__game_state = None # поле крестиков-ноликов
    
    def user_step(self, position):
        '''
        Ход юзера
        '''
        return self.__game_state
    
    def bot_step(self, position):
        '''
        Ход бота
        '''
        return self.__game_state
    
    def print_current_state(self):
        '''
        Выводит текущее состояние игровой доски в консоль
        '''
        print(self.__game_state)

