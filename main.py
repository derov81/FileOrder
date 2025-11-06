import os
import shutil
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Словарь для классификации файлов по расширениям
FILE_CATEGORIES = {
    "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff'],
    "Documents": ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.md', '.rtf'],
    "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz', '.iso'],
    "Audio": ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'],
    "Video": ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
    "Scripts": ['.py', '.js', '.html', '.css', '.php', '.json', '.xml'],
    "Executables": ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'],
    "Torrents": ['.torrent'],
}

def create_folders(destination_path, categories):
    for category in categories:
        category_path = os.path.join(destination_path, category)
        try:
            os.makedirs(category_path, exist_ok=True)
            logger.info(f"Папка создана или уже существует: {category_path}")
        except OSError as e:
            logger.error(f"Ошибка при создании папки {category_path}: {e}")

def get_file_category(file_extension):
    #Определяет категорию файла по его расширению
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension.lower() in extensions:
            return category
    return "Other" # Для файлов с неизвестными расширениями


def organize_downloads_folder(downloads_path=None):
    """
    Основная функция для организации файлов в папке Загрузки.

    Args:
        downloads_path (str): Путь к папке Загрузки. Если None, используется стандартная папка.
    """
    # Определяем путь к папке Загрузки
    if downloads_path is None:
        # Стандартный путь для Windows, для Linux/Mac нужно изменить
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    # Проверяем существование папки Загрузки
    if not os.path.exists(downloads_path):
        logger.error(f"Папка Загрузки не найдена: {downloads_path}")
        return

    logger.info(f"Начинаем организацию папки: {downloads_path}")

    # Создаем папки для категорий
    create_folders(downloads_path, list(FILE_CATEGORIES.keys()) + ["Other"])

    # Получаем список файлов и папок в папке Загрузки
    try:
        items = os.listdir(downloads_path)
    except OSError as e:
        logger.error(f"Ошибка при чтении содержимого папки: {e}")
        return

    moved_count = 0
    error_count = 0

    for item in items:
        item_path = os.path.join(downloads_path, item)

        # Пропускаем папки категорий и системные файлы
        if (os.path.isdir(item_path) and item in FILE_CATEGORIES.keys()) or item.startswith('.'):
            continue

        # Обрабатываем только файлы
        if os.path.isfile(item_path):
            # Получаем расширение файла
            _, file_extension = os.path.splitext(item)

            # Определяем категорию
            category = get_file_category(file_extension)

            # Целевой путь для перемещения
            destination_folder = os.path.join(downloads_path, category)
            destination_path = os.path.join(destination_folder, item)

            try:
                # Перемещаем файл
                shutil.move(item_path, destination_path)
                logger.info(f"Перемещен: {item} -> {category}/")
                moved_count += 1

            except Exception as e:
                logger.error(f"Ошибка при перемещении {item}: {e}")
                error_count += 1

    logger.info(f"Организация завершена! Перемещено файлов: {moved_count}, ошибок: {error_count}")


def organize_archives(downloads_path=None):
    """
    Дополнительная функция: распаковывает архивы в подпапку с тем же именем.
    """
    if downloads_path is None:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    archives_path = os.path.join(downloads_path, "Archives")

    if not os.path.exists(archives_path):
        return

    for archive in os.listdir(archives_path):
        archive_path = os.path.join(archives_path, archive)

        if os.path.isfile(archive_path):
            # Создаем папку для распаковки (без расширения)
            folder_name = os.path.splitext(archive)[0]
            extract_path = os.path.join(archives_path, folder_name)

            try:
                os.makedirs(extract_path, exist_ok=True)

                # Распаковываем архив
                if archive.endswith('.zip'):
                    import zipfile
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)
                elif archive.endswith('.tar.gz') or archive.endswith('.tar'):
                    import tarfile
                    with tarfile.open(archive_path, 'r:*') as tar_ref:
                        tar_ref.extractall(extract_path)

                logger.info(f"Архив распакован: {archive} -> Archives/{folder_name}/")

            except Exception as e:
                logger.error(f"Ошибка при распаковке {archive}: {e}")


if __name__ == "__main__":
    try:
        # Основная организация файлов
        organize_downloads_folder()

        # Дополнительно: распаковка архивов
        organize_archives()

        print("Скрипт успешно выполнен! Проверьте папку Загрузки.")

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print("Произошла ошибка при выполнении скрипта. Подробности в логе.")