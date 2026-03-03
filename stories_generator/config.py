"""Загрузка и валидация конфигурации из config.json."""

import json
from pathlib import Path

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Конфигурация одной модели (текст или изображение)."""
    url: str = Field(description="Base URL API")
    model: str = Field(description="Имя модели")
    api_key: str = Field(description="API-ключ")


class VideoConfig(BaseModel):
    """Настройки генерации видео."""
    width: int = Field(default=1080, description="Ширина видео в пикселях")
    height: int = Field(default=1920, description="Высота видео в пикселях")
    slide_duration: float = Field(default=5.0, description="Длительность одного слайда в секундах")
    fps: int = Field(default=30, description="Кадры в секунду")


class AppConfig(BaseModel):
    """Полная конфигурация приложения."""
    text_model: ModelConfig = Field(description="Модель для текстовой генерации")
    image_model: ModelConfig = Field(description="Модель для генерации изображений")
    video: VideoConfig = Field(default_factory=VideoConfig, description="Настройки видео")


def load_config(config_path: str | Path = "config.json") -> AppConfig:
    """Загружает конфигурацию из JSON-файла.

    Args:
        config_path: Путь к файлу config.json.

    Returns:
        Валидированный объект AppConfig.

    Raises:
        FileNotFoundError: Если файл не найден.
        pydantic.ValidationError: Если конфигурация невалидна.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return AppConfig.model_validate(data)
