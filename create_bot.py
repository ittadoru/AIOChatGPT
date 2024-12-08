from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from storages.pickleStorage import PickleStorage
from deep_translator import GoogleTranslator
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from dotenv import load_dotenv
import os

# Настройка логгера
logger = logging.getLogger(__name__)

# Загружаем переменные из .env файла
load_dotenv()

# Получение токена и админов из конфигурации
token = os.getenv('TOKEN')
admins = [int(admin_id) for admin_id in os.getenv('ADMINS').split(',')]

# Инициализация хранилища, переводчика и планировщика
storage = PickleStorage('state_data.pkl')  # Хранилище для сохранения состояния
translator = GoogleTranslator  # Инициализация переводчика Google
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')  # Планировщик задач

# Создание объекта бота и диспетчера
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=storage)

# Логирование успешной инициализации бота
logger.info("Бот успешно инициализирован.")
