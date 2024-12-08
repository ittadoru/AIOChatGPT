from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ContentType

from model.model_chatgpt import model_response
from model.model_vision import model_picture
from model.model_coder import model_coder

from log import logger
from create_bot import bot, storage
from handlers.command_handlers import change_model_command, reset, set_mode, clear_all_user_data


ollama_router = Router()

@ollama_router.message(F.text)
async def ollama_response(message: Message):
    """
    Обрабатывает текстовые сообщения, определяя команду или модель для обработки.
    """
    
    # Проверяем, началась ли сессия с пользователем
    if await storage.get_state(message.from_user.id) != "started":
        await message.answer("Для начала общения с ботом, напишите /start")
        return

    # Обработка команд
    if message.text.startswith('/re'):
        await reset(message)
        return
    elif message.text.startswith('/se'):
        await set_mode(message)
        return
    elif message.text.startswith('/cl'):
        await clear_all_user_data(message)
        return
    elif message.text.startswith('/ch'):
        await change_model_command(message)
        return
    
    # Обработка текстовых сообщений в зависимости от выбранной модели
    user_model = await storage.get_model(message.from_user.id)
    if user_model == "ChatGPT":
        await model_response(message)
    elif user_model == "Vision":
        await message.answer("Пожалуйста, отправьте фото.")
    elif user_model == "Coder":
        await model_coder(message)


@ollama_router.message(F.photo)
async def ollama_photo(message: Message):
    """
    Обрабатывает фото, если выбранная модель поддерживает работу с изображениями.
    """
    
    # Если выбраны модели ChatGPT или Coder, запрашиваем текст
    if await storage.get_model(message.from_user.id) in ["ChatGPT", "Coder"]:
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return
    
    # Если выбрана модель Vision, передаем изображение для обработки
    await model_picture(message)
