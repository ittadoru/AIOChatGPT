import ollama
from asyncio import to_thread

from create_bot import storage, translator, bot
from log import logger


MAX_HISTORY_LENGTH = 45

system_message = """You are a conversational assistant designed for answering general questions and providing information in a friendly and engaging manner.

You are **not** capable of handling programming-related tasks such as code generation, debugging, or providing code fixes.

If the user requests anything related to programming or code, you must **always** respond with the following message:
'Please switch to the "Coder" model by typing /set_mode and selecting "Coder". This model is specifically designed for coding tasks.'

Your role is focused on non-programming tasks, so kindly direct any coding-related queries to the appropriate model.
'"""

async def model_response(message):
    """Обрабатывает ответ модели, переводя вход и выход для модели, управляет историей диалога и возвращает ответ пользователю."""
    user_input = message.text
    user_id = message.from_user.id

    # Уведомление пользователя о процессе генерации ответа
    stream_message = await message.answer('⏳ Генерирую ответ...')
    
    # Переводим ввод пользователя на английский язык для корректной обработки моделью
    try:
        user_input_en = translator(source=storage.get_language(user_id), target='en').translate(user_input)        
    except Exception as e:
        bot.edit_message_text(
            chat_id=stream_message.chat.id,
            message_id=stream_message.message_id,
            text="⛔ Произошла ошибка при переводе ответа. Попробуйте позже или смените язык.",
            parse_mode=None
        )
        logger.error(f"Ошибка при переводе ответа: {e}")

    try:
        

        # Получаем данные пользователя (история, режим)
        user_data = await storage.get_data(user_id)

        # Инициализация истории для нового пользователя
        if 'history' not in user_data:
            user_data['history'] = []

        # Получаем режим пользователя (короткий или подробный ответ)
        mode = await storage.get_mode(user_id)

        # Добавляем инструкцию в историю в зависимости от режима
        if mode == 'short':
            user_data['history'].append({"role": "system", "content": f"Please provide a very, very much short answer. {system_message}"})
        else:
            user_data['history'].append({"role": "system", "content": system_message})

        # Добавляем сообщение пользователя в историю
        user_data['history'].append({"role": "user", "content": user_input_en})

        # Генерация ответа моделью
        try:
            response = await to_thread(
                ollama.chat,  # Передаем функцию без немедленного вызова
                model="llama3.1",
                messages=user_data['history'],
                stream=False
            )
            finally_response = response['message']['content']
            logger.info(f"Ответ модели ChatGPT для пользователя {user_id} успешно получен")
        except Exception as e:
            # Ошибка при вызове модели
            finally_response = "⛔ Извините, произошла ошибка при генерации ответа. Попробуйте позже."
            logger.error(f"Ошибка при вызове ollama.chat: {e}")

        # Переводим ответ модели
        finally_response = translator(source='en', target=storage.get_language(user_id)).translate(finally_response)

        # Обновляем историю с ответом модели
        user_data['history'].append({"role": "assistant", "content": finally_response})

        # Обрезаем историю, если она превышает максимальную длину
        if len(user_data['history']) > MAX_HISTORY_LENGTH:
            user_data['history'] = user_data['history'][-MAX_HISTORY_LENGTH:]

        # Сохраняем обновленную историю в хранилище
        await storage.set_data(user_id, user_data)

        # Отправляем ответ пользователю
        await bot.edit_message_text(
            chat_id=stream_message.chat.id,
            message_id=stream_message.message_id, 
            text=finally_response,
            parse_mode=None
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
