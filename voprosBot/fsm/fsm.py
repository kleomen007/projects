from aiogram.fsm.state import State, StatesGroup

# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMpost(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    fill_channal = State()        # Состояние ожидания ввода имени
    fill_name = State()
    fill_message = State()         # Состояние ожидания ввода возраста
    