import asyncio

from create_bot import bot, dp, scheduler, storage

from handlers.response_handler import ollama_router
from handlers.command_handlers import command_router

from workTime.delete_images import delete_all_images

from log import logger


async def main():
    try:
        # Запланировать выполнение задачи каждый день в 3 часа ночи
        logger.info("Запланированы задачи для удаления данных и фотографий.")
        scheduler.add_job(storage.clear_all_user_data, 'cron', hour=3, minute=0)
        scheduler.add_job(delete_all_images, 'cron', hour=3, minute=0, args=["photos"])

        # Запустите планировщик
        scheduler.start()
        logger.info("Планировщик задач запущен.")

        # Регистрируем роутеры
        dp.include_router(command_router)
        dp.include_router(ollama_router)
        logger.info("Роутеры успешно зарегистрированы.")

        # Удаление вебхука и начало получения обновлений
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        logger.info(f"Бот запущен. Storage: {storage}")

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")
        # Уведомление пользователю о проблемах с запуском бота
        # В зависимости от того, как вы уведомляете пользователей, добавьте соответствующий код

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")