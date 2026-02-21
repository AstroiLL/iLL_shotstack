# Fast-Clip - Техническое описание проекта

## Обзор

Fast-Clip - Python-приложение для автоматической сборки видео из клипов с использованием Shotstack API. Приложение поддерживает Shotstack-native JSON формат и Markdown с табличным представлением timeline.

## Архитектура

### Структура проекта

```
shotstack/
├── fast_clip/                    # Основной пакет
│   ├── __init__.py
│   ├── check/                    # Валидация скриптов
│   │   ├── __init__.py          # Экспорты модуля
│   │   ├── __main__.py          # CLI entry point
│   │   ├── checker.py           # ScriptChecker класс
│   │   └── validator.py         # Функции валидации
│   ├── uploader.py              # Загрузка файлов (Shotstack Ingest API)
│   ├── timeline_builder.py      # Обработка placeholders в Shotstack JSON
│   ├── shotstack_client.py      # API клиент для рендеринга
│   └── assembler.py             # Главный оркестратор
│
├── assemble.py                  # CLI для сборки видео
├── build.sh                     # Bash скрипт для быстрого запуска
├── check.py                     # Валидатор Shotstack-native JSON
├── convert_script.py            # Конвертер MD → Shotstack JSON
│
├── .env                         # Конфигурация окружения
├── .env.example                 # Шаблон конфигурации
├── pyproject.toml               # Зависимости проекта
└── uv.lock                      # Lock файл uv
```

### Поток данных (Template + Merge Workflow)

```
Markdown Script → convert_script.py → Shotstack Template JSON → assemble.py
                                           ↓                           ↓
                                    Template + Merge array       Validation
                                           ↓                           ↓
                                     {{placeholders}}            Upload files
                                           ↓                           ↓
                                     Merge fields               Replace {{}}
                                           ↓                           ↓
                                     Render request             Download
                                           ↓                           ↓
                                     Shotstack API              Result
```

## Компоненты

### 1. Конвертер (`convert_script.py`)

**Назначение:** Преобразование Markdown скриптов в Shotstack Template JSON и обратно.

**Процесс конвертации MD → JSON:**
1. Парсинг заголовков (name, resources_dir, soundtrack и др.)
2. Парсинг таблицы с колонками: Text, Description, Clip, Timing, Duration, Effect, Music effect, Sound effect
3. Генерация структуры Shotstack Template JSON с `{{resources_dir/file}}` placeholders
4. Создание merge массива для замены placeholders на URL

**Процесс конвертации JSON → MD:**
1. Извлечение данных из template.timeline и template.output
2. Восстановление таблицы с текстовыми оверлеями
3. Сопоставление аудио треков с видео по timing

**Особенности:**
- **Автоопределение направления**: по расширению файла (.md → .json, .json → .md)
- **Индексация**: при существовании выходного файла добавляется индекс (script_1.json, script_2.json)
- **Поддерживаемые эффекты**: fade, fadeFast, slideLeft, slideRight, wipe, zoom, zoomIn, zoomOut, kenBurns
- **Фильтры**: boost, greyscale, contrast, muted, negative, darken, lighten

### 2. Uploader (`fast_clip/uploader.py`)

**Назначение:** Загрузка локальных видео-файлов в Shotstack через Ingest API.

**Основные методы:**
- `upload(file_path)` - загрузка одного файла с ожиданием обработки
- `_get_signed_url()` - получение signed URL для загрузки
- `_wait_for_file_ready()` - polling статуса обработки (до 60 сек)

**Важно:** Shotstack требует время для обработки загруженных файлов. Метод `_wait_for_file_ready()` делает polling API каждые 2 секунды до получения статуса "ready".

### 3. Timeline Builder (`fast_clip/timeline_builder.py`)

**Назначение:** Замена `{{placeholder}}` на реальные URL загруженных файлов через merge workflow.

**Ключевые функции:**
- Рекурсивный поиск placeholders в template JSON
- Замена `{{resources_dir/filename}}` на URL из merge массива
- Поддержка template структуры (timeline внутри template объекта)
- Удаление служебных полей (`name`, `resourcesDir`) перед отправкой

**Workflow:**
1. Получение template JSON с `{{placeholders}}`
2. Загрузка файлов через Ingest API
3. Создание merge массива: `[{"find": "Video_01/clip.mp4", "replace": "https://..."}]`
4. Отправка на рендеринг с template + merge

**Пример:**
```json
// Template вход:
{
  "template": {
    "timeline": {
      "tracks": [{
        "clips": [{
          "asset": {"src": "{{Video_01/clip.mp4}}"}
        }]
      }]
    }
  },
  "merge": [{"find": "Video_01/clip.mp4", "replace": ""}]
}

// После обработки merge:
{
  "id": "template-id",
  "merge": [{"find": "Video_01/clip.mp4", "replace": "https://shotstack.io/..."}]
}
```

### 4. Shotstack Client (`fast_clip/shotstack_client.py`)

**Назначение:** HTTP клиент для Shotstack Edit API.

**Методы:**
- `render(edit_data)` - POST /render, возвращает render_id
- `get_status(render_id)` - GET /render/{id}, проверка статуса
- `wait_for_render(render_id, callback)` - polling до завершения
- `download(url, output_path)` - скачивание готового видео

**Статусы рендеринга:**
- `queued` - в очереди
- `fetching` - загрузка ассетов
- `rendering` - рендеринг
- `done` - готово
- `failed` - ошибка

### 5. Assembler (`fast_clip/assembler.py`)

**Назначение:** Главный оркестратор, объединяющий все компоненты с поддержкой template + merge workflow.

**Процесс сборки:**
1. Загрузка Shotstack Template JSON скрипта
2. Проверка формата (template с merge vs direct URL)
3. Извлечение ресурсов из template.timeline.tracks[].clips[].asset.src
4. Сбор уникальных файлов из merge массива
5. Загрузка всех файлов (видео + аудио) через Uploader
6. Создание merge данных с реальными URL
7. Отправка на рендеринг через ShotstackClient с template + merge
8. Ожидание завершения (polling)
9. Скачивание результата

**Поддержка форматов:**
- **Template + Merge**: JSON с `{"template": {...}, "merge": [...]}`
- **Direct URL**: JSON с прямыми URL в src (устаревший формат)

### 6. Check Module (`fast_clip/check/`)

**Назначение:** Валидация Shotstack Template JSON скриптов перед обработкой.

**Проверки:**
- Валидность JSON
- Наличие template и merge полей
- Существование файлов в resourcesDir
- Поддерживаемые transitions, effects, filters
- Корректность aspect_ratio, format, fps
- Валидность длительности клипов
- Корректность аудио клипов (type, src, volume)

**Поддерживаемые значения:**
- Transitions: fade, fadeFast, slideLeft, slideRight, zoom и др.
- Effects: zoomIn, zoomOut, kenBurns
- Filters: boost, greyscale, contrast, muted, negative, darken, lighten
- Aspect Ratios: 9:16, 16:9, 1:1, 4:5, 4:3
- Formats: mp4, mov, webm, gif
- Asset Types: video, image, audio

## Форматы данных

### Markdown Script Format (v2)

```markdown
## name: project_name
## resources_dir: Content
## soundtrack: music.mp3
## soundtrack_volume: 0.5
## background: "#000000"

| # | Text | Description | Clip | Timing | Duration | Effect | Music effect | Sound effect |
|---|------|-------------|------|--------|----------|--------|--------------|--------------|
| 1 | Привет! | Аватар | avatar.mp4 | 00:00:000-00:03:000 | 3.0s | ZoomIn | | |
| 2 | Как дела? | Аватар | avatar.mp4 | 00:03:000-00:05:500 | 2.5s | | | click.wav |
| 3 | Смотри | Видео | content.mp4 | 00:05:500-00:08:000 | 2.5s | | | whoosh.wav |

## output_format: mp4
## resolution: 1080p
## aspect_ratio: 9:16
## fps: 30
```

**Описание колонок:**
- `Text` - Текст для оверлея на видео
- `Description` - Описание сцены (не в видео)
- `Clip` - Имя файла видео
- `Timing` - Временной интервал (MM:SS:mmm-MM:SS:mmm)
- `Duration` - Длительность клипа
- `Effect` - Визуальный эффект (ZoomIn, FadeIn, FadeOut)
- `Music effect` - Эффект для фоновой музыки
- `Sound effect` - Звуковой эффект

### Shotstack-native JSON Format

```json
{
  "name": "project_name",
  "resourcesDir": "Video_01",
  "timeline": {
    "soundtrack": {
      "src": "{{Video_01/music.mp3}}",
      "effect": "fadeIn",
      "volume": 0.5
    },
    "background": "#000000",
    "tracks": [{
      "clips": [{
        "asset": {
          "type": "video",
          "src": "{{Video_01/clip.mp4}}",
          "trim": 0,
          "volume": 1.0
        },
        "start": "auto",
        "length": 5.0,
        "transition": {"in": "fadeFast", "out": "slideLeft"},
        "effect": "zoomIn",
        "filter": "boost"
      }]
    }]
  },
  "output": {
    "format": "mp4",
    "resolution": "1080p",
    "aspectRatio": "9:16",
    "fps": 30,
    "thumbnail": {"capture": 1}
  }
}
```

## Shotstack API Integration

### Ingest API (Загрузка)

```
POST /ingest/stage/upload        → получение signed URL
PUT  <signed_url>                → загрузка файла
GET  /ingest/stage/sources/{id}  → проверка статуса обработки
```

**Особенности:**
- Signed URL действителен ограниченное время
- После загрузки файл обрабатывается (конвертация, анализ)
- Для рендеринга нужен URL из поля `source`, а не сам signed URL

### Edit API (Рендеринг)

```
POST /edit/stage/render          → отправка на рендеринг
GET  /edit/stage/render/{id}     → проверка статуса
```

**Формат запроса (Shotstack-native):**
```json
{
  "timeline": {
    "soundtrack": {...},
    "background": "#000000",
    "tracks": [{
      "clips": [{
        "asset": {"type": "video", "src": "url", "trim": 0, "volume": 1.0},
        "start": "auto",
        "length": 5.0,
        "transition": {"in": "fadeFast", "out": "slideLeft"},
        "effect": "zoomIn",
        "filter": "boost"
      }]
    }]
  },
  "output": {
    "format": "mp4",
    "resolution": "1080p",
    "aspectRatio": "9:16",
    "fps": 30
  }
}
```

## Конфигурация

### Переменные окружения (.env)

```bash
SHOTSTACK_API_KEY=xxx        # Обязательно
```

### Зависимости (pyproject.toml)

```toml
[project]
requires-python = ">=3.13"
dependencies = [
    "pydantic",        # Валидация данных
    "requests",        # HTTP клиент
    "python-dotenv",   # Загрузка .env
    "ruff",            # Линтер
    "mypy",            # Type checker
]
```

## Разработка

### Установка dev-зависимостей

```bash
uv sync
```

### Код-стайл

- **Formatter:** ruff (PEP 8 compliant, 100 символов)
- **Type hints:** обязательны для всех функций
- **Docstrings:** Google-style
- **Naming:** snake_case (functions), PascalCase (classes)

### Типичные команды

```bash
# Проверка типов
uv run mypy .

# Линтинг
uv run ruff check .
uv run ruff check --fix .

# Форматирование
uv run ruff format .

# Конвертация MD в JSON
uv run python convert_script.py script.md

# Валидация
uv run python check.py script.json -v

# Сборка видео
uv run python assemble.py script.json -v
```

## Расширение функциональности

### Добавление нового transition

1. Добавить в `VALID_TRANSITIONS` в `convert_script.py` и `check.py`:
```python
VALID_TRANSITIONS = {"fade", "fadeFast", "newEffect"}
```

2. Обновить документацию в README.md

### Поддержка нового типа ассета

1. Обновить `build_clip()` в `convert_script.py` для определения типа
2. Проверить поддержку в `fast_clip/uploader.py`
3. Обновить валидацию в `check.py`

## Известные ограничения

- Максимум 10 клипов в timeline (ограничение валидатора)
- Нет поддержки сложной аудио микшировки (только фоновая музыка)
- Требуется интернет-соединение для работы с API
- На бесплатном тарифе Shotstack есть ограничения

## Отладка

### Включение verbose режима

```bash
uv run python assemble.py script.json -v
uv run python check.py script.json -v
```

### Логирование HTTP запросов

Добавить в код:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Проверка статуса рендера

```bash
curl -H "x-api-key: $SHOTSTACK_API_KEY" \
  https://api.shotstack.io/edit/stage/render/<render_id>
```

## Troubleshooting

### Ошибка "Access to file denied"

Причина: Используется неправильный URL файла.
Решение: URL должен быть получен из `GET /ingest/stage/sources/{id}`,
а не из signed URL для загрузки.

### Timeout при загрузке

Причина: Файл слишком большой или медленное соединение.
Решение: Увеличить таймаут в `_wait_for_file_ready()`.

### Render failed

Причина: Неправильный формат timeline или отсутствующие ассеты.
Решение: Проверить скрипт через `check.py -v`.

### Неизвестный эффект/переход

Причина: Используется эффект, не поддерживаемый Shotstack.
Решение: Проверить список VALID_TRANSITIONS/VALID_EFFECTS/VALID_FILTERS
и использовать только допустимые значения.

## Контакты и ресурсы

- Shotstack Docs: https://shotstack.io/docs/api/
- API Reference: https://shotstack.io/docs/api/api
- Python версия: 3.13+
- Менеджер пакетов: uv
