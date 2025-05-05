from aiogram.fsm.state import State, StatesGroup

class NotificationSettings(StatesGroup):
    frequency = State()
    parameter = State()
    filter_type = State()
    threshold = State()
    city = State()
