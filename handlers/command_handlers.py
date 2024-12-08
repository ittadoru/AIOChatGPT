from keyboards.change_keyboards import mode_keyboard, model_keyboard, language_keyboard
from create_bot import storage, admins

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardRemove

from filters.selections import ModeSelection
from log import logger

command_router = Router()

@command_router.message(CommandStart())
async def start(message: Message):
    """
    Обрабатывает команду /start, инициируя сессию с пользователем.
    Устанавливает начальные параметры пользователя: режим и модель.
    """
    try:
        # Устанавливаем начальный статус пользователя
        await storage.set_state(message.from_user.id, "started")
        await storage.set_mode(message.from_user.id, "short")
        await storage.set_model(message.from_user.id, "ChatGPT")
        await message.answer(f'🖐 Привет {message.from_user.first_name}! Я бот, который помогает тебе общаться с ChatGPT!')
        logger.info(f"Пользователь {message.from_user.id} по имени {message.from_user.first_name} начал использование бота.")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при запуске бота. Попробуйте позже.")

@command_router.message(Command('reset_history'))
async def reset(message: Message):
    """
    Обрабатывает команду /reset_history, очищая историю общения с ботом.
    """

    await storage.clear_chat_history(message.from_user.id)
    await message.answer('✔ Ваша история общения с ботом была очищена!')

@command_router.message(Command('set_mode'))
async def set_mode(message: Message, state: FSMContext):
    """
    Обрабатывает команду /set_mode, предлагая пользователю выбрать режим.
    """

    try:
        await message.answer("Выберите режим:", reply_markup=mode_keyboard)
        await state.set_state(ModeSelection.waiting_for_mode)
    except Exception as e:
        logger.error(f"Ошибка при установке режима для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при установке режима. Попробуйте снова позже.")


@command_router.message(ModeSelection.waiting_for_mode)
async def handle_mode_selection(message: Message, state: FSMContext):
    """
    Обрабатывает выбор режима пользователем.
    """
    try:
        if message.text in ["Краткие (рекомендуется)", "Детальные (медленно)"]:
            # Сохраняем выбранный режим
            mode = "detailed" if "Детальные (медленно)" in message.text else "short"
            await storage.set_mode(message.from_user.id, mode)
            # Убираем клавиатуру
            await message.answer(f"✔ Режим установлен: {mode.capitalize()}", reply_markup=ReplyKeyboardRemove())
            # Выходим из состояния
            await state.clear()
        else:
            await message.answer("⚠ Некорректный выбор. Пожалуйста, выберите один из предложенных режимов.")
    except Exception as e:
        logger.error(f"Ошибка при выборе режима для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при установке режима. Попробуйте снова позже.")

    

@command_router.message(Command('clear_all_user_data'))
async def clear_all_user_data(message: Message):
    """
    Обрабатывает команду /clear_all_user_data, очищая всю пользовательскую информацию.
    Доступно только администраторам.
    """
    
    user_id = message.from_user.id
    try:
        if user_id in admins:
            await storage.clear_all_user_data()
            await message.answer("✔ Вся история пользователей была успешно удалена.")
            logger.info(f"Администратор {user_id} удалил всю историю пользователей.")
        else:
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
    except Exception as e:
        logger.error(f"Ошибка при удалении всей истории пользователей администратором {user_id}: {e}")
        await message.answer(f"❌ Произошла ошибка при удалении истории: {e}", parse_mode=None)

@command_router.message(Command('change_model'))
async def change_model_command(message: Message, state: FSMContext):
    """
    Обрабатывает команду /change_model, предлагая пользователю выбрать модель.
    """
    try:
        await message.answer("Выберите модель:", reply_markup=model_keyboard)
        await state.set_state(ModeSelection.waiting_for_change)
    except Exception as e:
        logger.error(f"Ошибка при изменении модели для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при изменении модели. Попробуйте снова позже.")

# Обработка выбора модели
@command_router.message(ModeSelection.waiting_for_change)
async def handle_model_selection(message: Message, state: FSMContext):
    """
    Обрабатывает выбор модели пользователем.
    """
    try:
        selected_model = message.text.strip()  # Получаем текст кнопки

        if selected_model in ["ChatGPT", "Vision", "Coder"]:
            await storage.set_model(message.from_user.id, selected_model)
            await storage.clear_chat_history(message.from_user.id)
            await message.answer(
                f"✔ Модель изменена на {selected_model}.",
                reply_markup=ReplyKeyboardRemove()
            )
            # Сообщения в зависимости от выбранной модели
            if selected_model == "Vision":
                await message.answer("📷 Отправьте фото, а я попытаюсь разглядеть что на нём изображено (не отправляйте откровенные фото)")
                await message.answer("⚡ Предупреждение \nЭта модель может отвечать несколько минут и в целом нестабильна, проявите терпение")
            elif selected_model == "Coder":
                await message.answer("💻 Ну, отправьте свой говнокод, я попытаюсь его исправить")
            elif selected_model == "ChatGPT":
                await message.answer("👋 Давай поговорим о твоих мыслях, я тебя слушаю (нет)")
            await state.clear()
        else:
            await message.answer("⚠ Некорректный выбор. Пожалуйста, выберите одну из предложенных моделей.")
    except Exception as e:
        logger.error(f"Ошибка при изменении модели для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при изменении модели. Попробуйте снова позже.")

@command_router.message(Command('clear_all_images'))
async def clear_all_images(message: Message):
    """
    Обрабатывает команду /clear_all_images, очищая все изображения пользователей.
    Доступно только администраторам.
    """
    user_id = message.from_user.id
    try:
        if user_id in admins:
            import os

            imgs = os.listdir("photos")
            for img in imgs:
                os.remove(f"photos/{img}")

            await message.answer("✔ Все изображения были успешно удалены.")
            logger.info(f"Администратор {user_id} удалил все изображения.")
        else:
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
    except Exception as e:
        logger.error(f"Ошибка при удалении всех изображений администратором {user_id}: {e}")
        await message.answer(f"❌ Произошла ошибка при удалении изображений: {e}", parse_mode=None)

@command_router.message(Command('set_language'))
async def set_language(message: Message, state: FSMContext):
    """
    Обрабатывает команду /set_language, предлагая пользователю выбрать язык.
    """
    try:
        await message.answer("Выберите язык:", reply_markup=language_keyboard)
        await state.set_state(ModeSelection.waiting_for_language)
    except Exception as e:
        logger.error(f"Ошибка при установке языка для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при установке языка. Попробуйте снова позже.")


@command_router.message(ModeSelection.waiting_for_language)
async def handle_language_selection(message: Message, state: FSMContext):
    """
    Обрабатывает выбор языка пользователем.
    """
    try:
        if message.text in ["English", "Русский"]:
            # Сохраняем выбранный язык
            language = "en" if "English" in message.text else "ru"
            await storage.set_language(message.from_user.id, language)
            # Убираем клавиатуру
            await message.answer(f"✔ Язык установлен: {language.capitalize()}", reply_markup=ReplyKeyboardRemove())
            # Выходим из состояния
            await state.clear()
        else:
            await message.answer("⚠ Некорректный выбор. Пожалуйста, выберите один из предложенных языков.")
    except Exception as e:
        logger.error(f"Ошибка при выборе языка для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при установке языка. Попробуйте снова позже.")