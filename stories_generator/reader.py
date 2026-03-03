"""Чтение текстовых материалов из папки."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def read_materials(folder_path: str | Path) -> str:
    """Читает все текстовые файлы из указанной папки.

    Файлы сортируются по имени. Содержимое объединяется с разделителями
    (имя файла используется как заголовок секции).

    Args:
        folder_path: Путь к папке с материалами.

    Returns:
        Объединённый текст всех файлов.

    Raises:
        FileNotFoundError: Если папка не существует.
        ValueError: Если в папке нет подходящих файлов.
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Папка не найдена: {folder}")
    if not folder.is_dir():
        raise ValueError(f"Указанный путь не является папкой: {folder}")

    files = sorted(
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        raise ValueError(
            f"В папке {folder} нет файлов с расширениями {SUPPORTED_EXTENSIONS}"
        )

    sections: list[str] = []
    for file_path in files:
        logger.info("Читаю файл: %s", file_path.name)
        content = file_path.read_text(encoding="utf-8")
        sections.append(f"=== {file_path.name} ===\n\n{content}")

    combined = "\n\n---\n\n".join(sections)
    logger.info("Прочитано %d файлов, общий объём: %d символов", len(files), len(combined))
    return combined
