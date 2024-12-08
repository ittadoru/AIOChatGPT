from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

mode_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Краткие (рекомендуется)")],
                [KeyboardButton(text="Детальные (медленно)")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
      )

model_keyboard = ReplyKeyboardMarkup(
      keyboard =[
                [KeyboardButton(text="ChatGPT")],
                [KeyboardButton(text="Vision")],
                [KeyboardButton(text="Coder")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

language_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Русский")],
                [KeyboardButton(text="English")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
)