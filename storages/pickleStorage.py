from log import logger

import pickle
from pathlib import Path

from aiogram.fsm.storage.base import BaseStorage, StorageKey
import aiofiles

import asyncio

class PickleStorage(BaseStorage):
    def __init__(self, file_path: str = "state_data.pkl"):
        """Инициализация класса PickleStorage.
        
        Создает файл для хранения данных, если его нет.
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            # Создаем файл асинхронно, если он не существует
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._init_file())

    async def _init_file(self):
        """Создает новый пустой файл с данными в формате pickle."""
        try:
            async with aiofiles.open(self.file_path, "wb") as file:
                await file.write(pickle.dumps({}))
            logger.info(f"Файл {self.file_path} успешно создан.")
        except Exception as e:
            logger.error(f"Ошибка при создании файла {self.file_path}: {e}")

    async def _read_data(self) -> dict:
        """Чтение данных из файла."""
        try:
            async with aiofiles.open(self.file_path, "rb") as file:
                file_data = await file.read()
            return pickle.loads(file_data)
        except Exception as e:
            logger.error(f"Ошибка при чтении данных из файла {self.file_path}: {e}")
            return {}

    async def _write_data(self, data: dict):
        """Запись данных в файл."""
        try:
            async with aiofiles.open(self.file_path, "wb") as file:
                await file.write(pickle.dumps(data))
        except Exception as e:
            logger.error(f"Ошибка при записи данных в файл {self.file_path}: {e}")

    async def set_state(self, key: StorageKey, state: str | None = None):
        """Устанавливает состояние для пользователя."""
        data = await self._read_data()
        data.setdefault(str(key), {})["state"] = state
        await self._write_data(data)

    async def get_state(self, key: StorageKey):
        """Получает состояние пользователя."""
        data = await self._read_data()
        return data.get(str(key), {}).get("state")
    
    async def set_language(self, key: StorageKey, language: str | None = None):
        """Устанавливает язык для пользователя."""
        data = await self._read_data()
        data.setdefault(str(key), {})["language"] = language
        await self._write_data(data)

    async def get_language(self, key: StorageKey):
        """Получает язык пользователя."""
        data = await self._read_data()
        return data.get(str(key), {}).get("language")

    async def set_mode(self, key: StorageKey, mode: str | None = None):
        """Устанавливает режим для пользователя."""
        data = await self._read_data()
        data.setdefault(str(key), {})["mode"] = mode
        logger.info(f"Установлен режим для пользователя {key}: {mode}")
        await self._write_data(data)

    async def get_mode(self, key: StorageKey):
        """Получает режим пользователя."""
        data = await self._read_data()
        return data.get(str(key), {}).get("mode")

    async def set_model(self, key: StorageKey, model: str | None = None):
        """Устанавливает модель для пользователя."""
        data = await self._read_data()
        data.setdefault(str(key), {})["model"] = model
        logger.info(f"Установлена модель для пользователя {key}: {model}")
        await self._write_data(data)

    async def get_model(self, key: StorageKey):
        """Получает модель пользователя."""
        data = await self._read_data()
        return data.get(str(key), {}).get("model")

    async def set_data(self, key: StorageKey, data: dict):
        """Устанавливает произвольные данные для пользователя."""
        all_data = await self._read_data()
        all_data.setdefault(str(key), {})["data"] = data
        await self._write_data(all_data)

    async def get_data(self, key: StorageKey):
        """Получает произвольные данные пользователя."""
        data = await self._read_data()
        return data.get(str(key), {}).get("data", {})

    async def update_data(self, key: StorageKey, data: dict):
        """Обновляет произвольные данные пользователя."""
        all_data = await self._read_data()
        user_data = all_data.setdefault(str(key), {}).get("data", {})
        user_data.update(data)
        all_data[str(key)]["data"] = user_data
        await self._write_data(all_data)
        return user_data

    async def clear_chat_history(self, key: StorageKey):
        """Очищает историю чата пользователя."""
        try:
            user_data = await self.get_data(key)
            user_data['history'] = []  # Очищаем историю

            await self.set_data(key, user_data)
            logger.info(f"История пользователя {key} была очищена.")
        except Exception as e:
            logger.error(f"Ошибка при очистке истории пользователя {key}: {e}")

    async def clear_all_user_data(self):
        """Очищает все данные пользователей."""
        try:
            data = await self._read_data()
            user_ids = list(data.keys())
            for user_id in user_ids:
                user_data = data.get(user_id, {}).get('data', {})
                if 'history' in user_data:
                    user_data['history'] = []  # Очищаем историю
                    await self.clear_chat_history(user_id)

            logger.info("История всех пользователей была очищена.")
        except Exception as e:
            logger.error(f"Ошибка при очистке всех историй пользователей: {e}")

    async def close(self):
        """Закрытие хранилища (в данном случае не требуется)."""
        pass