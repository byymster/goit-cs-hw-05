import asyncio
from pathlib import Path
import shutil
import argparse
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("file_sorter.log", mode='a'), logging.StreamHandler()]
)


async def copy_file(file_path: Path, dest_folder: Path):
    """Копіює файл до папки залежно від його розширення"""
    try:
        # Визначення папки для розширення
        extension = file_path.suffix[1:]  # Позбавляється точки у розширенні
        if not extension:
            extension = "unknown"  # Для файлів без розширення

        target_dir = dest_folder / extension
        target_dir.mkdir(parents=True, exist_ok=True)

        # Асинхронне копіювання файлу
        target_file = target_dir / file_path.name
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, shutil.copy2, file_path, target_file)

        logging.info(f"Copied {file_path} to {target_file}")
    except Exception as e:
        logging.error(f"Failed to copy {file_path}: {e}")


async def read_folder(source_folder: Path, dest_folder: Path):
    """Читає всі файли у вихідній папці та копіює їх асинхронно"""
    try:
        tasks = []
        # Рекурсивний пошук файлів
        for item in source_folder.rglob('*'):
            if item.is_file():
                tasks.append(copy_file(item, dest_folder))

        # Виконання всіх задач
        await asyncio.gather(*tasks)
        logging.info("File sorting completed successfully.")
    except Exception as e:
        logging.error(f"Error while reading folder {source_folder}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument("source_folder", type=str, help="Вихідна папка (source folder)(default: input)", nargs='?', default="./input")
    parser.add_argument("dest_folder", type=str, help="Цільова папка (output folder)(default: output)", nargs='?', default="./output")
    args = parser.parse_args()

    source_folder = Path(args.source_folder)
    dest_folder = Path(args.dest_folder)

    if not source_folder.exists() or not source_folder.is_dir():
        logging.error("Вказана вихідна папка не існує або не є директорією.")
        return

    dest_folder.mkdir(parents=True, exist_ok=True)

    try:
        # Запуск основного асинхронного процесу
        asyncio.run(read_folder(source_folder, dest_folder))
    except Exception as e:
        logging.error(f"Critical error: {e}")


if __name__ == "__main__":
    main()