"""HTTP-клиент для API генерации изображений (v1/images/generations)."""

import base64
import logging
from pathlib import Path

import httpx

from stories_generator.config import ModelConfig

logger = logging.getLogger(__name__)


class ImageClient:
    """Клиент для генерации изображений через v1/images/generations API."""

    def __init__(self, config: ModelConfig, timeout: float = 180.0):
        """Инициализация клиента.

        Args:
            config: Конфигурация модели (url, model, api_key).
            timeout: Таймаут запроса в секундах.
        """
        self.config = config
        self.base_url = config.url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def generate_image(
        self,
        prompt: str,
        output_path: str | Path,
        size: str = "1024x1792",
    ) -> Path:
        """Генерирует изображение по промпту и сохраняет в файл.

        Args:
            prompt: Текстовый промпт для генерации.
            output_path: Путь для сохранения изображения.
            size: Размер изображения (по умолчанию 1024x1792 — portrait).

        Returns:
            Путь к сохранённому файлу.
        """
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "n": 1,
            "size": size,
        }

        url = f"{self.base_url}/images/generations"
        logger.info(
            "Image запрос: model=%s, size=%s, prompt=%s...",
            self.config.model,
            size,
            prompt[:80],
        )

        response = self._client.post(url, json=payload)
        if response.status_code != 200:
            logger.error("Image ошибка %d: %s", response.status_code, response.text)
        response.raise_for_status()

        data = response.json()
        image_data = data["data"][0]

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if "b64_json" in image_data:
            image_bytes = base64.b64decode(image_data["b64_json"])
            output_path.write_bytes(image_bytes)
        elif "url" in image_data:
            # Скачиваем по URL
            img_response = self._client.get(image_data["url"])
            img_response.raise_for_status()
            output_path.write_bytes(img_response.content)
        else:
            raise ValueError("Ответ API не содержит ни b64_json, ни url")

        logger.info("Изображение сохранено: %s", output_path)
        return output_path

    def close(self):
        """Закрывает HTTP-клиент."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
