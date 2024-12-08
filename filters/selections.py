from aiogram.filters.state import State, StatesGroup

# Определение состояний
class ModeSelection(StatesGroup):
    """
    Состояния для выбора режима и модели пользователем.
    Используется для обработки команд в процессе взаимодействия с ботом.
    """

    waiting_for_mode = State()  # Ожидание выбора режима (краткий или детализированный)
    waiting_for_change = State()  # Ожидание изменения модели (ChatGPT, Vision, Coder)
    waiting_for_language = State()  # Ожидание выбора языка