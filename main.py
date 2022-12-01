from itertools import product
import time
from console_progressbar import ProgressBar
import re
import random
from collections import Counter

#Работа сделана студентами группы БСМО-02-22 Бардиным, Болдышевым, Верховых, Макаровым.

# Размер шага (влияет на скорость обучения)
LEARNING_RATE = 0.01
PROGRESS_BAR = ProgressBar(total=100, prefix='Прогресс: ', suffix='', decimals=0, length=50, fill='|', zfill='/')


# Заменяет в строке символ по индексу
def replace_char_at_index(org_str, index, replacement):
    new_str = org_str
    if index < len(org_str):
        new_str = org_str[0:index] + replacement + org_str[index + 1:]
    return new_str


# Класс "Поле крестиков-ноликов"
class Field:
    def __init__(self, size=3):
        self.size = size
        # Инициализируем историю игр (для статистики)
        self.game_history = {-1: 0, 1: 0, 2: 0}

    # Возвращает список пустых клеток
    @staticmethod
    def get_empty_cells(state):
        return [_.start() for _ in re.finditer('0', state)]

    # Проверяет поле на наличие победителя
    # Возвращает:
    #    -1 - если никто не выиграл и закончились свободные клетки
    #     0 - если никто не выиграл и есть свободные клетки
    #     1 - если победил игрок №1
    #     2 - если победил игрок №2
    @staticmethod
    def win_state(state):
        # все выигрыши через центральную точку [1])[1]) (4 шт)
        if (int(state[4]) > 0 and (
                int(state[0]) == int(state[4]) and int(state[8]) == int(state[4]) or int(state[2]) == int(
                state[4]) and int(state[6]) == int(state[4]) or int(state[3]) == int(state[4]) and int(state[3]) == int(
                state[5]) or int(state[1]) == int(state[4]) and int(state[1]) == int(state[7]))):
            return (int(state[4]))
        # все выигрыши через левую верхнюю клетку [0])[0]) (2 шт)
        elif (int(state[0]) > 0 and (
                int(state[0]) == int(state[1]) and int(state[0]) == int(state[2]) or int(state[0]) == int(
                state[3]) and int(state[0]) == int(state[6]))):
            return (int(state[0]))
        # все выигрыши через правую нижнюю клетку [2])[2]) (2 шт)
        elif (int(state[8]) > 0 and (
                int(state[6]) == int(state[7]) and int(state[6]) == int(state[8]) or int(state[2]) == int(
                state[5]) and int(state[2]) == int(state[8]))):
            return (int(state[8]))
        # если никто на выиграл и закончились клетки
        elif len(Field.get_empty_cells(state)) == 0:
            return -1
        return 0

    # Обучение агента (игра с другим агентом)
    def start_learning(self, player1, player2, steps=100):
        for game_num in (range(steps)):
            # Начальное состояние поля
            state = '000000000'
            # Пока есть свободные клетки и никто не выиграл игроки по очереди делают шаги
            while Field.win_state(state) == 0:
                old_state = state
                state = player1.make_decission(state)
                # Перерасчет ценностей
                player2.refresh_values(old_state, state)
                # print(old_state,state,self.win_state(state))
                # Проверка, что прошлый игрок не победил на последнем шаге
                if Field.win_state(state) == 0:
                    old_state = state
                    state = player2.make_decission(state)
                    player1.refresh_values(old_state, state)
                    # print(old_state,state,self.win_state(state))

            # Как только игра закончилась, отправить финальное состояние игрокам для пересчета ценностей
            # player1.refresh_values(state)
            # player2.refresh_values(state)
            # print(game_num,' игра. Выиграл игрок №',Field.win_state(state))
            # print(state[0],state[1],state[2])
            # print(state[3],state[4],state[5])
            # print(state[6],state[7],state[8])
            # print('_______________________')
            player1.refresh_values(old_state, state)
            player2.refresh_values(old_state, state)
            # Показать прогресс-бар
            if (game_num / steps) * 100 % 5 == 0:
                # print('Обучение закончено на ', (game_num/(steps - 1))*100, '%')
                PROGRESS_BAR.print_progress_bar((game_num / steps) * 100)
            self.game_history[Field.win_state(state)] = self.game_history[Field.win_state(state)] + 1
        PROGRESS_BAR.print_progress_bar(100)

    def human_print(self, state):
        state_for_human = state.replace('1', 'X').replace('2', 'O')
        for char_num in range(9):
            if state_for_human[char_num] == '0':
                state_for_human = replace_char_at_index(state_for_human, char_num, str(char_num))
        self.print_field(state_for_human)

    def human_decission(self, state, human_number):
        print('Текущее поле:')
        self.human_print(state)
        human_step = input("Введи номер клетки для хода: ")
        return replace_char_at_index(state, int(human_step), str(human_number))

    def start_game(self, agent, human):
        # Начальное состояние поля
        state = '000000000'
        # Пока есть свободные клетки и никто не выиграл игроки по очереди делают шаги
        while Field.win_state(state) == 0:
            if (human == 'X'):
                human_number = 1
                state = self.human_decission(state, human_number)
                # Проверка, что прошлый игрок не победил на последнем шаге
                if Field.win_state(state) == 0:
                    state = agent.make_decission(state)
            elif (human == 'O'):
                human_number = 2
                state = agent.make_decission(state)
                # Проверка, что прошлый игрок не победил на последнем шаге
                if Field.win_state(state) == 0:
                    state = self.human_decission(state, human_number)
        print('Конец игры: ')
        self.human_print(state)

    # Вывести поле
    def print_field(self, state):
        print(state[0], state[1], state[2])
        print(state[3], state[4], state[5])
        print(state[6], state[7], state[8])


# Класс игрок
class Player:
    def __init__(self, number):
        # Номер игрока
        self.number = number
        # Таблица ценностей (состояний)
        self.states = {}
        # Шаги во время игры
        self.steps = []
        # Заполнить стартовую таблицу ценностей
        self.fill_matrix()

    # Заполнение таблицы ценностей начальными значениями
    def fill_matrix(self):
        for roll in product([0, 1, 2], repeat=9):
            # states = {}
            key = ''.join(str(x) for x in roll)
            winner = Field.win_state(key)
            # Состояния выигрыша
            if winner == self.number:
                self.states[key] = 1
            # Стандартное состояние
            elif winner == 0:
                self.states[key] = 0.5
            # Состояние проигрыша
            else:
                self.states[key] = 0
        # return states

    # Возвращает доступные шаги для игрока в текущем состоянии и их ценности
    def get_avail_states(self, current_state):
        avail_states = {}
        # Пустые клетки, на которые можно пойти
        empty_cells = [_.start() for _ in re.finditer('0', current_state)]
        # Получение списка возможных следующих состояний
        for cell in empty_cells:
            avail_state = replace_char_at_index(current_state, cell, str(self.number))
            avail_states[avail_state] = self.states[avail_state]
        # print(avail_states)
        return avail_states

    # Принятие решения о следующем шаге
    def make_decission(self, current_state):
        avail_states = self.get_avail_states(current_state)
        # Делать ли разведочный шаг? (с заданной вероятностью) True = да, False = нет
        exploration_move = random.random() <= 0.05
        # Если шаг не разведочный -> выбираем следующее состояние с наибольшей ценностью
        if not exploration_move:
            # Поиск наивысшей цены среди возможных шагов
            max_value = max(avail_states.values())
            # Поиск всех ходов с наивысшей ценой
            max_value_states = {}  # Словарь ходов с наивысшей ценой
            # Заполнить словарь ходов с наивысшей ценой
            for state in avail_states.keys():
                if avail_states[state] == max_value:
                    max_value_states[state] = avail_states[state]
            # Вернуть следующее состояние с максимальной ценой (если несколько - выбрать рандомно)
            new_state, max_value = random.choice(list(max_value_states.items()))
            # self.steps.append(new_state)
            return new_state
        # Если шаг разведочный -> выбираем случайный ход
        else:
            new_state, random_value = random.choice(list(avail_states.items()))
            self.steps.append(new_state)
            return new_state

    # Перерасчет ценностей состояний
    def refresh_values(self, n_state, n1_state):
        # finish_value = self.states[final_state]
        # Для каждого шага в прошедшей игре перерасчитать ценность по формуле:
        # Новое_значение_ценности = Старое_значение_ценности + Размер_шага * (Ценность_последнего_шага - Старое_значение_ценности)
        # Ценность_последнего_шага равна 1 (если игрок выиграл) 0,5 (если ничья) 0 (если проиграл)
        # for step in self.steps:
        # old_value = self.states[n_state]
        self.states[n_state] = self.states[n_state] + LEARNING_RATE * (self.states[n1_state] - self.states[n_state])
        # print('Перерасчет. ',self.number,' player. ',self.states[n_state],'=',self.states[n1_state] )
        # self.steps.clear()

    # Получить топ N состояний с наибольшей ценностью для игрока
    def get_top_n_states(self, top=5):
        states_except_wins = {}
        for key in self.states.keys():
            if self.states[key] < 1:
                states_except_wins[key] = self.states[key]
        k = Counter(states_except_wins)
        high = k.most_common(top)
        return high


# Инициализация двух игроков
player1 = Player(1)
player2 = Player(2)
# Иницилизация игрового поля
tic_tac_toe = Field()
print('Первый этап обучения')
# Обучение агента (250 000 игр за крестик и 250 000 игр за нолик)
tic_tac_toe.start_learning(player1, player2, 50000)
print()
# print('Второй этап обучения')
# tic_tac_toe.start_learning(player2, player1, 250000)

# Вывести историю игр при обучении
# print(tic_tac_toe.game_history)

# Вывсти наиболее ценные состояния игроков после обучения
# print(player1.get_top_n_states(20))
# print(player2.get_top_n_states(20))

### PVE ###
while True:
    human_chouse = input("Выбирай за кого играть! Введи X или O (английские буквы): ")
    if human_chouse == 'X':
        tic_tac_toe.start_game(player2, human_chouse)
    elif human_chouse == 'O':
        tic_tac_toe.start_game(player1, human_chouse)
    else:
        "Введи правильную букву"
    next_game = input("Не получилось... Введи Y или N (английские буквы): ")
    if next_game == 'N':
        break;
