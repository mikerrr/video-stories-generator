"""Главный пайплайн генерации сторис с чекпоинтами."""

import logging
from pathlib import Path

from stories_generator.config import load_config
from stories_generator.reader import read_materials
from stories_generator.llm_client import LLMClient
from stories_generator.image_client import ImageClient
from stories_generator.planner import plan_and_review
from stories_generator.slide_renderer import generate_image_prompts, render_slides
from stories_generator.video import assemble_video
from stories_generator.models import StoryOutline, SlideImagePrompts

logger = logging.getLogger(__name__)

# Имена файлов-чекпоинтов
OUTLINE_FILE = "slides_outline.json"
IMAGE_PROMPTS_FILE = "image_prompts.json"


def generate_story(
    input_folder: str | Path,
    config_path: str | Path = "config.json",
) -> Path:
    """Генерирует видео-сторис из текстовых материалов.

    Каждый этап сохраняет результат в файл внутри input_folder.
    При повторном запуске этапы с готовыми файлами пропускаются.

    Чекпоинты:
    - slides_outline.json   — план слайдов (после планирования и ревью)
    - image_prompts.json    — промпты для генерации изображений
    - slide_XX.png          — сгенерированные изображения слайдов
    - story.mp4             — финальный ролик

    Args:
        input_folder: Путь к папке с материалами (.txt, .md файлы).
        config_path: Путь к файлу config.json.

    Returns:
        Путь к созданному MP4-файлу.
    """
    input_folder = Path(input_folder)
    output_path = input_folder / "story.mp4"
    outline_path = input_folder / OUTLINE_FILE
    prompts_path = input_folder / IMAGE_PROMPTS_FILE

    # 1. Загрузить конфиг
    logger.info("=" * 60)
    logger.info("STORIES GENERATOR — Начинаю генерацию")
    logger.info("=" * 60)
    logger.info("Входная папка: %s", input_folder)
    logger.info("Конфиг: %s", config_path)

    config = load_config(config_path)
    logger.info("Конфиг загружен: text_model=%s, image_model=%s",
                config.text_model.model, config.image_model.model)

    # 2. Прочитать материалы
    logger.info("-" * 40)
    logger.info("ШАГ 1: Чтение материалов")
    logger.info("-" * 40)
    material_text = read_materials(input_folder)

    # 3-4. Планирование и ревью слайдов
    logger.info("-" * 40)
    logger.info("ШАГ 2: Планирование и ревью слайдов")
    logger.info("-" * 40)

    if outline_path.exists():
        logger.info(">>> Найден чекпоинт: %s — пропускаю планирование", outline_path.name)
        outline = StoryOutline.model_validate_json(outline_path.read_text(encoding="utf-8"))
        logger.info("Загружен план: тема='%s', слайдов=%d", outline.topic, len(outline.slides))
    else:
        with LLMClient(config.text_model) as llm:
            outline = plan_and_review(llm, material_text)
        outline_path.write_text(outline.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("План сохранён в: %s", outline_path.name)

    # 5. Генерация промптов для изображений
    logger.info("-" * 40)
    logger.info("ШАГ 3: Генерация промптов для изображений")
    logger.info("-" * 40)

    if prompts_path.exists():
        logger.info(">>> Найден чекпоинт: %s — пропускаю генерацию промптов", prompts_path.name)
        image_prompts = SlideImagePrompts.model_validate_json(
            prompts_path.read_text(encoding="utf-8")
        )
        logger.info("Загружено %d промптов", len(image_prompts.prompts))
    else:
        with LLMClient(config.text_model) as llm:
            image_prompts = generate_image_prompts(llm, outline)
        prompts_path.write_text(
            image_prompts.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info("Промпты сохранены в: %s", prompts_path.name)

    # 6. Генерация изображений (с пропуском уже готовых)
    logger.info("-" * 40)
    logger.info("ШАГ 4: Генерация изображений")
    logger.info("-" * 40)

    image_paths = render_slides(
        image_client_config=config.image_model,
        image_prompts=image_prompts,
        output_dir=input_folder,
    )

    # 7. Сборка видео
    logger.info("-" * 40)
    logger.info("ШАГ 5: Сборка видео")
    logger.info("-" * 40)

    result_path = assemble_video(
        image_paths=image_paths,
        output_path=output_path,
        video_config=config.video,
    )

    logger.info("=" * 60)
    logger.info("ГОТОВО! Ролик сохранён: %s", result_path)
    logger.info("=" * 60)

    return result_path
