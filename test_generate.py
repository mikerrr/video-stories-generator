"""Тестовый скрипт для проверки библиотеки Stories Generator."""

import logging
import sys
from datetime import datetime
from pathlib import Path

from stories_generator import generate_story


def main():

    # Имя лог-файла с датой и временем запуска
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"run_{timestamp}.log"

    # Настройка логирования: консоль + файл
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%H:%M:%S"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )

    logging.info("Лог сохраняется в: %s", log_file)

    # Параметры
    input_folder = "test_story2"
    config_path = "config_my.json"

    # Проверяем наличие входных данных
    if not Path(input_folder).exists():
        print(f"ОШИБКА: Папка '{input_folder}' не найдена!")
        sys.exit(1)

    if not Path(config_path).exists():
        print(f"ОШИБКА: Файл конфигурации '{config_path}' не найден!")
        sys.exit(1)

    print(f"Запуск генерации сторис из папки: {input_folder}")
    print(f"Конфигурация: {config_path}")
    print()

    try:
        result = generate_story(input_folder, config_path)
        print()
        print(f"Генерация завершена успешно!")
        print(f"Ролик сохранён: {result}")
    except Exception as e:
        print(f"ОШИБКА при генерации: {e}")
        logging.exception("Подробности ошибки:")
        sys.exit(1)


if __name__ == "__main__":
    main()
