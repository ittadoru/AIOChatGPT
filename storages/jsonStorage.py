import json
from pathlib import Path

from aiogram.fsm.storage.base import BaseStorage, StorageKey

from log import logger

class JSONStorage(BaseStorage):
    def __init__(self, file_path: str = "fsm_data.json"):
        """Инициализация класса JSONStorage.
        
        Создает файл для хранения данных в формате JSON, если его нет.
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            # Создаем новый файл с пустыми данными
            try:
                self.file_path.write_text(json.dumps({}))
                logger.info(f"Файл {self.file_path} был успешно создан.")
            except Exception as e:
                logger.error(f"Ошибка при создании файла {self.file_path}: {e}")

    def _read_data(self) -> dict:
        """Чтение данных из JSON файла."""
        try:
            with self.file_path.open("r") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Ошибка при чтении данных из файла {self.file_path}: {e}")
            return {}

    def _write_data(self, data: dict):
        """Запись данных в JSON файл."""
        try:
            with self.file_path.open("w") as file:
                json.dump(data, file, indent=4)
            logger.info(f"Данные успешно записаны в файл {self.file_path}.")
        except Exception as e:
            logger.error(f"Ошибка при записи данных в файл {self.file_path}: {e}")

    async def set_state(self, key: StorageKey, state: str | None = None):
        """Устанавливает состояние для пользователя."""
        data = self._read_data()
        data.setdefault(str(key), {})["state"] = state
        self._write_data(data)

    async def get_state(self, key: StorageKey):
        """Получает состояние пользователя."""
        data = self._read_data()
        return data.get(str(key), {}).get("state")

    async def set_data(self, key: StorageKey, data: dict):
        """Устанавливает произвольные данные для пользователя."""
        all_data = self._read_data()
        all_data.setdefault(str(key), {})["data"] = data
        self._write_data(all_data)

    async def get_data(self, key: StorageKey):
        """Получает произвольные данные пользователя."""
        data = self._read_data()
        return data.get(str(key), {}).get("data", {})

    async def update_data(self, key: StorageKey, data: dict):
        """Обновляет произвольные данные пользователя."""
        all_data = self._read_data()
        user_data = all_data.setdefault(str(key), {}).get("data", {})
        user_data.update(data)
        all_data[str(key)]["data"] = user_data
        self._write_data(all_data)
        return user_data

    async def close(self):
        """Закрытие хранилища (в данном случае не требуется)."""
        pass
