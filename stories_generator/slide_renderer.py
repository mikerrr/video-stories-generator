"""Генерация изображений для слайдов с текстом, вписанным в визуал."""

import logging
from pathlib import Path

from stories_generator.llm_client import LLMClient
from stories_generator.image_client import ImageClient
from stories_generator.config import ModelConfig
from stories_generator.models import StoryOutline, SlideImagePrompts

logger = logging.getLogger(__name__)

IMAGE_PROMPT_SYSTEM = """\
Ты — арт-директор, специализирующийся на визуальном контенте для Telegram Stories.

Твоя задача — создать промпты для генерации изображений для каждого слайда сторис.
Каждое изображение должно:
- Быть вертикальным (portrait, 9:16)
- Содержать текст слайда, ОРГАНИЧНО ВПИСАННЫЙ в изображение
- Текст должен быть КРУПНЫМ, легко читаемым на мобильном экране
- Визуал должен усиливать посыл текста, а не конфликтовать с ним
- Стиль: современный, профессиональный, привлекающий внимание

Важно: промпт должен быть на АНГЛИЙСКОМ языке.
Текст на изображении должен быть на РУССКОМ языке (точно как в плане слайда).

В промпте чётко указывай:
1. Стиль изображения
2. Композицию и расположение элементов
3. Точный текст, который нужно разместить на изображении
4. Где и как должен быть расположен текст
5. Цветовую палитру и настроение
"""


def generate_image_prompts(
    llm: LLMClient,
    outline: StoryOutline,
) -> SlideImagePrompts:
    """Генерирует промпты для изображений каждого слайда.

    Args:
        llm: Клиент LLM.
        outline: Одобренный план сторис.

    Returns:
        Промпты для генерации изображений.
    """
    outline_text = outline.model_dump_json(indent=2)

    messages = [
        {"role": "system", "content": IMAGE_PROMPT_SYSTEM},
        {
            "role": "user",
            "content": (
                "Создай промпты для генерации изображений для каждого "
                "слайда следующей сторис:\n\n"
                f"{outline_text}"
            ),
        },
    ]

    logger.info("Генерирую промпты для изображений...")
    prompts = llm.generate(messages, SlideImagePrompts, temperature=0.7)
    logger.info("Создано %d промптов для изображений", len(prompts.prompts))
    return prompts


def render_slides(
    image_client_config: ModelConfig,
    image_prompts: SlideImagePrompts,
    output_dir: Path,
    image_size: str = "1024x1536",
) -> list[Path]:
    """Генерирует изображения для всех слайдов. Пропускает уже готовые.

    Args:
        image_client_config: Конфигурация клиента генерации изображений.
        image_prompts: Промпты для генерации.
        output_dir: Директория для сохранения изображений.
        image_size: Размер генерируемых изображений.

    Returns:
        Список путей к изображениям (в порядке слайдов).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths: list[Path] = []
    slides_to_generate = []

    # Проверяем какие слайды уже есть
    for img_prompt in image_prompts.prompts:
        slide_num = img_prompt.slide_number
        output_path = output_dir / f"slide_{slide_num:02d}.png"
        image_paths.append(output_path)

        if output_path.exists():
            logger.info(">>> Слайд %d уже существует: %s — пропускаю", slide_num, output_path.name)
        else:
            slides_to_generate.append((img_prompt, output_path))

    if not slides_to_generate:
        logger.info("Все изображения уже сгенерированы")
        return image_paths

    logger.info("Нужно сгенерировать %d из %d изображений",
                len(slides_to_generate), len(image_prompts.prompts))

    # Генерируем только недостающие
    with ImageClient(image_client_config) as image_client:
        for img_prompt, output_path in slides_to_generate:
            slide_num = img_prompt.slide_number
            logger.info("Генерирую изображение для слайда %d...", slide_num)
            image_client.generate_image(
                prompt=img_prompt.prompt,
                output_path=output_path,
                size=image_size,
            )
            logger.info("Слайд %d готов: %s", slide_num, output_path.name)

    return image_paths
