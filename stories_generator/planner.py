"""Планирование и ревью слайдов через LLM."""

import logging

from stories_generator.llm_client import LLMClient
from stories_generator.models import StoryOutline, StoryReview

logger = logging.getLogger(__name__)

PLAN_SYSTEM_PROMPT = """\
Ты — эксперт по созданию коротких, цепляющих историй для Telegram Stories.

Твоя задача — на основе предоставленных материалов создать план сторис из 6-10 слайдов.

Требования к плану:
- Каждый слайд должен содержать КОРОТКИЙ, ёмкий текст (1-3 предложения максимум)
- Текст должен быть крупным и читаемым на мобильном экране
- История должна иметь чёткую структуру: зацепка → проблема → развитие → решение/вывод
- Визуальные описания должны быть на АНГЛИЙСКОМ языке (для генерации изображений)
- Визуал должен усиливать и дополнять текст, а не просто иллюстрировать его
- Текст на слайде должен быть органично вписан в визуал

Формат сторис: вертикальный (9:16), смотрят на телефоне.
"""

REVIEW_SYSTEM_PROMPT = """\
Ты — редактор и критик контента для социальных сетей.

Оцени предложенный план сторис по трём критериям (1-10):
1. Цельность — насколько слайды связаны между собой, есть ли логическая структура
2. Убедительность — насколько сильно история воздействует на читателя
3. Ясность — понятен ли посыл, нет ли перегруженности текстом

Если средний балл >= 7, поставь approved=true.
Если средний балл < 7, поставь approved=false и дай конкретные рекомендации.
"""

MAX_RETRIES = 2


def plan_slides(llm: LLMClient, material_text: str) -> StoryOutline:
    """Генерирует план слайдов на основе материалов.

    Args:
        llm: Клиент LLM.
        material_text: Объединённый текст всех материалов.

    Returns:
        Полный план сторис.
    """
    messages = [
        {"role": "system", "content": PLAN_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Создай план сторис на основе следующих материалов:\n\n"
                f"{material_text}"
            ),
        },
    ]

    logger.info("Генерирую план слайдов...")
    outline = llm.generate(messages, StoryOutline, temperature=0.8)
    logger.info(
        "План готов: тема='%s', слайдов=%d",
        outline.topic,
        len(outline.slides),
    )
    return outline


def review_slides(llm: LLMClient, outline: StoryOutline) -> StoryReview:
    """Проверяет план слайдов на цельность, убедительность и ясность.

    Args:
        llm: Клиент LLM.
        outline: План сторис для проверки.

    Returns:
        Результат ревью.
    """
    outline_text = outline.model_dump_json(indent=2)

    messages = [
        {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Оцени следующий план сторис:\n\n"
                f"{outline_text}"
            ),
        },
    ]

    logger.info("Провожу ревью плана...")
    review = llm.generate(messages, StoryReview, temperature=0.3)
    logger.info(
        "Ревью: цельность=%d, убедительность=%d, ясность=%d, approved=%s",
        review.overall_coherence,
        review.overall_persuasiveness,
        review.overall_clarity,
        review.approved,
    )
    return review


def plan_and_review(llm: LLMClient, material_text: str) -> StoryOutline:
    """Планирует слайды и проводит ревью с возможностью перепланирования.

    Если ревью не одобрено, перепланирует с учётом рекомендаций (до MAX_RETRIES раз).

    Args:
        llm: Клиент LLM.
        material_text: Объединённый текст всех материалов.

    Returns:
        Одобренный план сторис.
    """
    outline = plan_slides(llm, material_text)

    for attempt in range(MAX_RETRIES + 1):
        review = review_slides(llm, outline)

        if review.approved:
            logger.info("План одобрен на попытке %d", attempt + 1)
            return outline

        if attempt < MAX_RETRIES:
            logger.warning(
                "План не одобрен (попытка %d/%d). Перепланирую с учётом рекомендаций...",
                attempt + 1,
                MAX_RETRIES + 1,
            )
            messages = [
                {"role": "system", "content": PLAN_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Создай план сторис на основе следующих материалов:\n\n"
                        f"{material_text}"
                    ),
                },
                {
                    "role": "assistant",
                    "content": outline.model_dump_json(indent=2),
                },
                {
                    "role": "user",
                    "content": (
                        "Ревьюер дал следующие замечания, учти их и создай "
                        "улучшенный план:\n\n"
                        f"{review.summary}\n\n"
                        "Замечания по слайдам:\n"
                        + "\n".join(
                            f"- Слайд {s.slide_number}: {s.suggestion}"
                            for s in review.slides
                            if s.suggestion != "OK"
                        )
                    ),
                },
            ]
            outline = llm.generate(messages, StoryOutline, temperature=0.8)
        else:
            logger.warning(
                "План не одобрен после %d попыток. Используем лучший вариант.",
                MAX_RETRIES + 1,
            )

    return outline
