"""HTTP-клиент для OpenAI Chat Completions API."""

import json
import logging
from typing import TypeVar

import httpx
from pydantic import BaseModel

from stories_generator.config import ModelConfig

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Клиент для взаимодействия с LLM через OpenAI Chat Completions API.

    Поддерживает structured output через response_format.
    """

    def __init__(self, config: ModelConfig, timeout: float = 120.0):
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

    def generate(
        self,
        messages: list[dict[str, str]],
        response_model: type[T],
        temperature: float = 0.7,
    ) -> T:
        """Генерация ответа с structured output.

        Args:
            messages: Список сообщений в формате Chat Completions.
            response_model: Pydantic-модель для парсинга ответа.
            temperature: Температура генерации.

        Returns:
            Распарсенный объект Pydantic-модели.
        """
        json_schema = response_model.model_json_schema()
        schema_str = json.dumps(json_schema, ensure_ascii=False, indent=2)

        # Добавляем инструкцию по JSON-схеме в системное сообщение
        schema_instruction = (
            "\n\nОтвечай СТРОГО в формате JSON, соответствующем следующей схеме:\n"
            f"```json\n{schema_str}\n```\n"
            "Не добавляй никакого текста вне JSON. Только валидный JSON."
        )

        # Копируем сообщения и дополняем первое системное
        enriched_messages = []
        schema_injected = False
        for msg in messages:
            if msg["role"] == "system" and not schema_injected:
                enriched_messages.append({
                    "role": "system",
                    "content": msg["content"] + schema_instruction,
                })
                schema_injected = True
            else:
                enriched_messages.append(msg)

        if not schema_injected:
            enriched_messages.insert(0, {
                "role": "system",
                "content": "Ты — помощник, отвечающий в формате JSON." + schema_instruction,
            })

        payload = {
            "model": self.config.model,
            "messages": enriched_messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        url = f"{self.base_url}/chat/completions"
        logger.info("LLM запрос: model=%s, messages=%d", self.config.model, len(enriched_messages))

        response = self._client.post(url, json=payload)
        if response.status_code != 200:
            logger.error("LLM ошибка %d: %s", response.status_code, response.text)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        logger.debug("LLM ответ (raw): %s", content[:500])

        parsed = response_model.model_validate_json(content)
        logger.info("LLM ответ распарсен: %s", response_model.__name__)

        return parsed

    def generate_text(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """Генерация текстового ответа без structured output.

        Args:
            messages: Список сообщений в формате Chat Completions.
            temperature: Температура генерации.

        Returns:
            Текстовый ответ модели.
        """
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
        }

        url = f"{self.base_url}/chat/completions"
        logger.info("LLM text запрос: model=%s", self.config.model)

        response = self._client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        logger.info("LLM text ответ: %d символов", len(content))
        return content

    def close(self):
        """Закрывает HTTP-клиент."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
