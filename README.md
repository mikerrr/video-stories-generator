# Stories Generator

**🇷🇺 [Описание на русском](#описание) | 🇬🇧 [English description](#description)**

---

## Описание

Библиотека для автоматической генерации видео-сторис для Telegram из текстовых материалов.

### Как это работает

1. **Чтение материалов** — загружает `.txt` и `.md` файлы из указанной папки
2. **Планирование слайдов** — LLM анализирует материалы и создаёт план сторис (6–10 слайдов)
3. **Ревью плана** — LLM проверяет план на цельность, убедительность и ясность. При низкой оценке автоматически перепланирует (до 2 попыток)
4. **Генерация изображений** — для каждого слайда создаётся изображение с текстом, органично вписанным в визуал
5. **Сборка видео** — изображения объединяются в MP4-ролик формата 1080×1920 (portrait)

### Чекпоинты

Каждый этап сохраняет результат в папку с контентом. При повторном запуске готовые этапы пропускаются:

| Файл | Этап |
|---|---|
| `slides_outline.json` | План слайдов |
| `image_prompts.json` | Промпты для генерации изображений |
| `slide_01.png`, `slide_02.png`, ... | Сгенерированные изображения |
| `story.mp4` | Финальный ролик |

Для перегенерации этапа — удалите соответствующий файл.

### Установка

```bash
pip install -r requirements.txt
```

### Конфигурация

Создайте файл `config.json`:

```json
{
    "text_model": {
        "url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "api_key": "YOUR_API_KEY"
    },
    "image_model": {
        "url": "https://api.openai.com/v1",
        "model": "dall-e-3",
        "api_key": "YOUR_API_KEY"
    },
    "video": {
        "width": 1080,
        "height": 1920,
        "slide_duration": 5.0,
        "fps": 30
    }
}
```

- **text_model** — любая модель, совместимая с OpenAI Chat Completions API
- **image_model** — любая модель, совместимая с `/v1/images/generations`

### Использование

#### Как библиотека

```python
from stories_generator import generate_story

result = generate_story("путь/к/папке/с/материалами", "config.json")
print(f"Ролик: {result}")
```

#### Тестовый скрипт

```bash
python test_generate.py
```

### Пример работы

В папке `test_story2` находится пример работы библиотеки на основе статьи «6 полезных навыков, которым, к сожалению, не учат в школе».

**Сгенерированные артефакты:**
- 📄 Исходный текст: [`6 полезных навыков, которым, к сожалению, не учат в школе.md`](test_story2/6%20полезных%20навыков,%20которым,%20к%20сожалению,%20не%20учат%20в%20школе.md)
- 📝 План слайдов: [`slides_outline.json`](test_story2/slides_outline.json)
- 🎨 Промпты для генерации: [`image_prompts.json`](test_story2/image_prompts.json)
- 🖼 Изображения (10 штук): [`slide_01.png`](test_story2/slide_01.png) ... [`slide_10.png`](test_story2/slide_10.png)
- 🎬 Готовое видео: [`story.mp4`](test_story2/story.mp4)

### Структура проекта

```
stories_generator/
├── __init__.py          # Точка входа
├── models.py            # Pydantic-модели (structured output)
├── config.py            # Загрузка конфигурации
├── reader.py            # Чтение материалов из папки
├── llm_client.py        # Клиент OpenAI Chat Completions
├── image_client.py      # Клиент генерации изображений
├── planner.py           # Планирование и ревью слайдов
├── slide_renderer.py    # Генерация изображений слайдов
├── video.py             # Сборка MP4 (MoviePy)
└── pipeline.py          # Главный пайплайн
```

### Зависимости

- **pydantic** — structured output от LLM
- **httpx** — HTTP-запросы к API
- **moviepy** — сборка видео

---

## Description

A library for automatic generation of Telegram Stories videos from text materials.

### How It Works

1. **Read materials** — loads `.txt` and `.md` files from a specified folder
2. **Plan slides** — LLM analyzes the materials and creates a story plan (6–10 slides)
3. **Review plan** — LLM checks the plan for coherence, persuasiveness, and clarity. Automatically replans if the score is low (up to 2 retries)
4. **Generate images** — for each slide, an image is created with text organically embedded into the visual
5. **Assemble video** — images are combined into a 1080×1920 (portrait) MP4 video

### Checkpoints

Each stage saves its result to the content folder. On re-run, completed stages are skipped:

| File | Stage |
|---|---|
| `slides_outline.json` | Slide plan |
| `image_prompts.json` | Image generation prompts |
| `slide_01.png`, `slide_02.png`, ... | Generated images |
| `story.mp4` | Final video |

To regenerate a stage — delete the corresponding file.

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create a `config.json` file:

```json
{
    "text_model": {
        "url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "api_key": "YOUR_API_KEY"
    },
    "image_model": {
        "url": "https://api.openai.com/v1",
        "model": "dall-e-3",
        "api_key": "YOUR_API_KEY"
    },
    "video": {
        "width": 1080,
        "height": 1920,
        "slide_duration": 5.0,
        "fps": 30
    }
}
```

- **text_model** — any model compatible with OpenAI Chat Completions API
- **image_model** — any model compatible with `/v1/images/generations`

### Usage

#### As a library

```python
from stories_generator import generate_story

result = generate_story("path/to/materials/folder", "config.json")
print(f"Video: {result}")
```

#### Test script

```bash
python test_generate.py
```

### Example

The `test_story2` folder contains an example of the library's output based on a sample article.

**Generated artifacts:**
- 📄 Original text: [`6 полезных навыков, которым, к сожалению, не учат в школе.md`](test_story2/6%20полезных%20навыков,%20которым,%20к%20сожалению,%20не%20учат%20в%20школе.md)
- 📝 Slide plan: [`slides_outline.json`](test_story2/slides_outline.json)
- 🎨 Image prompts: [`image_prompts.json`](test_story2/image_prompts.json)
- 🖼 Images (10 slides): [`slide_01.png`](test_story2/slide_01.png) ... [`slide_10.png`](test_story2/slide_10.png)
- 🎬 Final video: [`story.mp4`](test_story2/story.mp4)

### Project Structure

```
stories_generator/
├── __init__.py          # Entry point
├── models.py            # Pydantic models (structured output)
├── config.py            # Configuration loader
├── reader.py            # Material reader
├── llm_client.py        # OpenAI Chat Completions client
├── image_client.py      # Image generation client
├── planner.py           # Slide planning & review
├── slide_renderer.py    # Slide image generation
├── video.py             # MP4 assembly (MoviePy)
└── pipeline.py          # Main pipeline
```

### Dependencies

- **pydantic** — structured LLM output
- **httpx** — HTTP requests to APIs
- **moviepy** — video assembly

---

## License

MIT
