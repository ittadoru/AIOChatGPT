import ollama

from create_bot import storage, bot
from asyncio import to_thread

from log import logger


MAX_HISTORY_LENGTH = 60

# Сообщение системы, которое будет включено в контекст
system_message = """You are a bot assistant who answers questions about programming. 
Always highlight the code in the response using triple back quotes (```) so that Telegram formats the code correctly.
To highlight the syntax, specify the programming language immediately after the first triple quotes. For example: ```python"""

async def model_coder(message):
    """
    Обрабатывает запрос пользователя по программированию, генерирует ответ с помощью модели и отправляет его в чат.
    """

    user_input = message.text  # Получаем текст пользователя
    user_id = message.from_user.id  # Получаем ID пользователя

    try:
        # Отправляем начальное сообщение о том, что код готовится
        stream_message = await message.answer('⌨ Мега код готовится...') 

        # Получаем данные пользователя
        user_data = await storage.get_data(user_id)

        # Инициализация истории для нового пользователя, если её нет
        if 'history' not in user_data:
            user_data['history'] = []

        # Получаем режим работы (короткий или детализированный)
        mode = await storage.get_mode(user_id)  

        # Добавляем системное сообщение с инструкциями
        user_data['history'].append({"role": "system", "content": f"Please provide a very, very much short answer. {system_message}"})

        # Добавляем сообщение пользователя в контекст
        user_data['history'].append({"role": "user", "content": user_input})

        # Обрабатываем запрос с помощью модели (в потоке, чтобы не блокировать основной цикл)
        try:
            # Выполнение запроса к модели в отдельном потоке
            response = await to_thread(
                ollama.chat,  # Передаем функцию, не вызывая её напрямую
                model="qwen2.5-coder:1.5b",  # Используем модель кодирования
                messages=user_data['history'],
                stream=False
            )

            # Извлекаем ответ от модели
            finally_response = response['message']['content']
            logger.info(f"Ответ модели Coder для пользователя {user_id} успешно получен")

        except Exception as e:
            # Обработка ошибок: если произошла ошибка при вызове модели
            finally_response = "⛔ Извините, произошла ошибка при генерации ответа. Попробуйте позже."
            logger.error(f"Ошибка при вызове ollama.chat: {e}")

        # Обновляем историю с ответом модели
        user_data['history'].append({"role": "assistant", "content": finally_response})

        # Очищаем историю, если она превышает максимальную длину
        if len(user_data['history']) > MAX_HISTORY_LENGTH:
            user_data['history'] = user_data['history'][-MAX_HISTORY_LENGTH:]

        # Сохраняем обновленное состояние пользователя
        await storage.set_data(user_id, user_data)

        # Отправляем ответ модели обратно пользователю
        await bot.edit_message_text(
            chat_id=stream_message.chat.id,
            message_id=stream_message.message_id, 
            text=finally_response,  # Ответ модели
        )

    except Exception as e:
        # Ловим ошибки на уровне всей функции
        logger.error(f"Ошибка при обработке запроса пользователя {user_id}: {e}")
        await bot.edit_message_text(
            chat_id=stream_message.chat.id,
            message_id=stream_message.message_id,
            text="☁ Произошла ошибка сервера. Попробуйте позже.",
            parse_mode=None
        )
