"""Pydantic-модели для structured output LLM."""

from pydantic import BaseModel, Field


class SlideOutline(BaseModel):
    """План одного слайда."""
    slide_number: int = Field(description="Номер слайда")
    title: str = Field(description="Короткий заголовок слайда (2-5 слов)")
    text: str = Field(description="Текст, который будет отображён на слайде (1-3 коротких предложения)")
    visual_description: str = Field(description="Описание визуала/картинки для слайда на английском языке")


class StoryOutline(BaseModel):
    """Полный план сторис."""
    topic: str = Field(description="Общая тема сторис")
    target_audience: str = Field(description="Целевая аудитория")
    slides: list[SlideOutline] = Field(description="Список слайдов")


class SlideReviewItem(BaseModel):
    """Рецензия на один слайд."""
    slide_number: int = Field(description="Номер слайда")
    coherence: int = Field(ge=1, le=10, description="Оценка цельности (1-10)")
    persuasiveness: int = Field(ge=1, le=10, description="Оценка убедительности (1-10)")
    clarity: int = Field(ge=1, le=10, description="Оценка ясности (1-10)")
    suggestion: str = Field(description="Рекомендация по улучшению (или 'OK' если всё хорошо)")


class StoryReview(BaseModel):
    """Ревью всей сторис."""
    overall_coherence: int = Field(ge=1, le=10, description="Общая цельность истории (1-10)")
    overall_persuasiveness: int = Field(ge=1, le=10, description="Общая убедительность (1-10)")
    overall_clarity: int = Field(ge=1, le=10, description="Общая ясность (1-10)")
    slides: list[SlideReviewItem] = Field(description="Рецензии на отдельные слайды")
    summary: str = Field(description="Общее заключение и рекомендации")
    approved: bool = Field(description="True если план готов к реализации, False если нужна доработка")


class ImagePrompt(BaseModel):
    """Промпт для генерации изображения слайда."""
    slide_number: int = Field(description="Номер слайда")
    prompt: str = Field(
        description=(
            "Полный промпт для генерации изображения на английском языке. "
            "Должен содержать описание визуала И текст, который должен быть "
            "органично вписан в изображение."
        )
    )


class SlideImagePrompts(BaseModel):
    """Промпты для генерации изображений всех слайдов."""
    prompts: list[ImagePrompt] = Field(description="Список промптов для каждого слайда")
