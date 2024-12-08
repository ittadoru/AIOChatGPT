import ollama

from create_bot import storage, bot, token

from asyncio import to_thread
import aiohttp

from log import logger
from PIL import Image

import io
import os

MAX_HISTORY_LENGTH = 15
PHOTO_SAVE_PATH = "photos"
URI_INFO = f"https://api.telegram.org/bot{token}/getFile?file_id="
URI = f"https://api.telegram.org/file/bot{token}/"

async def model_picture(message):
    """Обрабатывает фото от пользователя, генерирует ответ с использованием модели и обновляет историю."""
    user_id = message.from_user.id
    stream_message = None  # Инициализируем переменную заранее

    try:
        # Уведомление пользователя о процессе обработки фото
        stream_message = await message.answer('👀 Пытаюсь разглядеть...')

        # Получаем данные пользователя
        user_data = await storage.get_data(user_id)

        # Инициализация истории, если её нет
        if 'history' not in user_data:
            user_data['history'] = []

        if 'images' not in user_data:
            user_data['images'] = []

        # Получаем фото с Telegram
        file_id = message.photo[-1].file_id
        file_path = f"{PHOTO_SAVE_PATH}/{file_id}.png"
        
        # Добавляем ID фото в список
        user_data['images'].append(file_id)

        async with aiohttp.ClientSession() as session:
            # Получаем информацию о файле
            async with session.get(URI_INFO + file_id) as response:
                response_json = await response.json()
                img_path = response_json['result']['file_path']

            # Скачиваем изображение
            async with session.get(URI + img_path) as img_response:
                img_bytes = await img_response.read()

        # Сохраняем изображение с помощью Pillow
        img_buffer = io.BytesIO(img_bytes)
        img = Image.open(img_buffer)
        img.save(file_path, format="PNG")

        # Получаем текст (если имеется) и переводим его
        caption = message.caption if message.caption else "There is no text"

        # Добавляем системную инструкцию в историю
        user_data['history'].append({"role": "system", "content": "Please provide a short answer."})

        # Добавляем текст пользователя и путь к изображению в историю
        user_data['history'].append({"role": "user", "content": caption, 'images': [file_path]})

        # Отправляем запрос модели без потокового получения данных
        try:
            response = await to_thread(
                ollama.chat,
                model="llama3.2-vision",
                messages=user_data['history'],
                stream=False
            )
            finally_response = response['message']['content']
            logger.info(f"Ответ модели Vision для пользователя {user_id} успешно получен")
        except Exception as e:
            logger.error(f"Ошибка при вызове ollama.chat: {e}")
            await message.answer("⛔ Произошла ошибка при обработке фото. Попробуйте ещё раз.")
            return

        # Обновляем контекст с ответом модели
        user_data['history'].append({"role": "assistant", "content": finally_response})

        # Ограничиваем размер истории
        if len(user_data['history']) > MAX_HISTORY_LENGTH:
            user_data['history'] = user_data['history'][-MAX_HISTORY_LENGTH:]

        # Сохраняем обновленный контекст
        await storage.set_data(user_id, user_data)

        # Отправляем ответ пользователю, если предварительное сообщение было отправлено
        if stream_message:
            await bot.edit_message_text(
                chat_id=stream_message.chat.id,
                message_id=stream_message.message_id, 
                text=finally_response,
                parse_mode=None
            )


    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        if stream_message:
            await bot.edit_message_text(
                chat_id=stream_message.chat.id,
                message_id=stream_message.message_id,
                text="⛔ Извините, произошла ошибка при генерации ответа. Попробуйте позже.",
                parse_mode=None
            )
