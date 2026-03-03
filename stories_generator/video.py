"""Сборка видео из изображений слайдов с помощью MoviePy."""

import logging
from pathlib import Path

from moviepy import ImageClip, concatenate_videoclips

from stories_generator.config import VideoConfig

logger = logging.getLogger(__name__)


def assemble_video(
    image_paths: list[Path],
    output_path: Path,
    video_config: VideoConfig,
) -> Path:
    """Собирает видео из списка изображений.

    Args:
        image_paths: Пути к изображениям слайдов (в порядке показа).
        output_path: Путь для сохранения финального MP4-файла.
        video_config: Настройки видео (длительность слайда, fps, размер).

    Returns:
        Путь к созданному MP4-файлу.
    """
    if not image_paths:
        raise ValueError("Список изображений пуст")

    logger.info(
        "Собираю видео из %d изображений (%.1f сек/слайд, %d fps)...",
        len(image_paths),
        video_config.slide_duration,
        video_config.fps,
    )

    clips = []
    for img_path in image_paths:
        clip = ImageClip(str(img_path)).with_duration(video_config.slide_duration)
        clip = clip.resized((video_config.width, video_config.height))
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    final.write_videofile(
        str(output_path),
        fps=video_config.fps,
        codec="libx264",
        audio=False,
        logger=None,
    )

    # Освобождаем ресурсы
    for clip in clips:
        clip.close()
    final.close()

    total_duration = len(image_paths) * video_config.slide_duration
    logger.info(
        "Видео готово: %s (%.1f сек, %dx%d)",
        output_path,
        total_duration,
        video_config.width,
        video_config.height,
    )
    return output_path
