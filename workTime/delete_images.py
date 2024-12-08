from create_bot import storage
from log import logger


def delete_all_images(folder_path):
    try:
        logger.info("Начало удаления всех изображений")

        # Удалите все изображения из папки
        import shutil
        import os
        
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)

        # Логируем, что все изображения были удалены
        logger.info("Все изображения были удалены")
    except Exception as e:
        logger.error(f"Ошибка при удалении изображений: {e}")