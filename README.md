# Fast-Clip

Простой инструмент для создания видео из видео-клипов по JSON-скрипту.

## Что делает программа

Fast-Clip позволяет автоматически собирать видео из нескольких клипов с помощью облачного сервиса [Shotstack](https://shotstack.io/). Вы создаете JSON-скрипт, который описывает:

- Какие клипы использовать
- С какого момента начать и где закончить каждый клип
- Какие эффекты применить (плавное появление, затухание)
- Итоговое разрешение и формат

Программа загружает клипы в облако, собирает их в нужном порядке и скачивает готовое видео.

## Требования

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - менеджер пакетов
- API ключ от Shotstack (бесплатный тариф доступен)

## Установка

### 1. Установка uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Клонирование репозитория

```bash
git clone <repository-url>
cd shortstack
```

### 3. Установка зависимостей

```bash
uv sync
```

### 4. Настройка API ключа

Получите API ключ на [shotstack.io](https://shotstack.io/) (бесплатно).

```bash
# Скопируйте шаблон конфигурации
cp .env.example .env

# Отредактируйте .env и вставьте ваш API ключ
# SHOTSTACK_API_KEY=ваш_ключ_здесь
```

## Использование

### Быстрый старт

```bash
# Собрать видео из скрипта
./build.sh script_video_01.json

# С подробным выводом
./build.sh -v script_video_01.json

# Указать папку для сохранения
./build.sh -o ./output script_video_01.json
```

### Или через Python

```bash
uv run python assemble.py script_video_01.json -v
```

## Формат скрипта

Скрипт описывает сборку видео в формате JSON:

```json
{
  "name": "my_video",
  "resources_dir": "Video_01",
  "timeline": [
    {
      "id": 1,
      "resource": "clip_01.mp4",
      "time_start": "00:00",
      "time_end": "00:05",
      "start_effect": "fade_in",
      "start_duration": "3s",
      "end_effect": null,
      "end_duration": null
    },
    {
      "id": 2,
      "resource": "clip_02.mp4",
      "time_start": "00:00",
      "time_end": "00:07",
      "start_effect": null,
      "end_effect": "fade_out",
      "end_duration": "3s"
    }
  ],
  "result_file": "output.mp4",
  "output_format": "mp4",
  "resolution": "1080p",
  "orientation": "landscape"
}
```

### Описание полей

**Общие настройки:**
- `name` - название проекта
- `resources_dir` - папка с исходными видео
- `result_file` - имя выходного файла
- `output_format` - формат (mp4, mov, avi)
- `resolution` - разрешение (1080p, 720p, 480p)
- `orientation` - ориентация (landscape, portrait, square)

**Элементы timeline (видео-клипы):**
- `id` - порядковый номер
- `resource` - имя файла видео
- `time_start` - время начала (MM:SS или HH:MM:SS)
- `time_end` - время окончания
- `start_effect` - эффект начала: `fade_in`
- `end_effect` - эффект конца: `fade_out`
- `start_duration` / `end_duration` - длительность эффекта (например, "3s")

### Markdown формат

Скрипты можно писать и в Markdown:

```markdown
## name: my_video
## resources_dir: Video_01
## output_format: mp4
## resolution: 1080p

| # | Resources | Time | Start_Effect | Start_Duration | Effect_During | End_Effect | End_Duration | Description
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | clip_01.mp4 | 00:00 - 00:05 | fade in | 3 sec | | | |
| 2 | clip_02.mp4 | 00:00 - 00:07 | | | | fade out | 3 sec |

## result_file: output.mp4
```

Конвертировать MD в JSON:
```bash
uv run python convert_script.py script.md
```

## Проверка скрипта

Перед сборкой проверьте скрипт на ошибки:

```bash
uv run python check.py script_video_01.json -v
```

## Примеры

В репозитории есть примеры скриптов:
- `script_video_01.json` - пример с двумя клипами и эффектами
- `Video_01/` - папка с тестовыми видео

## Ограничения

- Максимум 10 клипов в одном видео
- Исходные видео должны быть в папке `resources_dir`
- Поддерживаемые форматы: mp4, mov, avi, mkv
- На бесплатном тарифе Shotstack есть ограничения на длительность и количество рендеров

## Получение помощи

```bash
# Справка по использованию
./build.sh --help

# Проверить версии
uv --version
python --version
```

## Лицензия

MIT
