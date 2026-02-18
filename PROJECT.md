# Fast-Clip - Техническое описание проекта

## Обзор

Fast-Clip - Python-приложение для автоматической сборки видео из клипов с использованием Shotstack API. Приложение поддерживает Shotstack-native JSON формат и Markdown с табличным представлением timeline.

## Архитектура

### Структура проекта

```
shortstack/
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

### Поток данных

```
Markdown Script → convert_script.py → Shotstack-native JSON → assemble.py
                                           ↓                      ↓
                                    TimelineBuilder        Validation
                                           ↓                      ↓
                                     Replace {{}}          Upload
                                           ↓                      ↓
                                    Shotstack JSON        Render
                                           ↓                      ↓
                                     Shotstack API      Download
```

## Компоненты

### 1. Конвертер (`convert_script.py`)

**Назначение:** Преобразование Markdown скриптов в Shotstack-native JSON.

**Процесс конвертации:**
1. Парсинг заголовков (name, resources_dir, soundtrack и др.)
2. Парсинг таблицы timeline
3. Генерация структуры Shotstack JSON с `{{resources_dir/file}}` placeholders

**Поддерживаемые эффекты:**
- Transitions: fade, fadeFast, slideLeft, slideRight, wipe, zoom и др.
- Effects: zoomIn, zoomOut, kenBurns
- Filters: boost, greyscale, contrast, muted, negative, darken, lighten

### 2. Uploader (`fast_clip/uploader.py`)

**Назначение:** Загрузка локальных видео-файлов в Shotstack через Ingest API.

**Основные методы:**
- `upload(file_path)` - загрузка одного файла с ожиданием обработки
- `_get_signed_url()` - получение signed URL для загрузки
- `_wait_for_file_ready()` - polling статуса обработки (до 60 сек)

**Важно:** Shotstack требует время для обработки загруженных файлов. Метод `_wait_for_file_ready()` делает polling API каждые 2 секунды до получения статуса "ready".

### 3. Timeline Builder (`fast_clip/timeline_builder.py`)

**Назначение:** Замена `{{placeholder}}` на реальные URL загруженных файлов.

**Ключевые функции:**
- Рекурсивный поиск placeholders в JSON
- Замена `{{resources_dir/filename}}` на URL
- Удаление служебных полей (`name`, `resourcesDir`) перед отправкой

**Пример:**
```json
// Вход:
{"asset": {"src": "{{Video_01/clip.mp4}}"}}

// Выход:
{"asset": {"src": "https://shotstack.io/.../clip.mp4"}}
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

**Назначение:** Главный оркестратор, объединяющий все компоненты.

**Процесс сборки:**
1. Загрузка Shotstack-native JSON скрипта
2. Извлечение ресурсов из timeline.tracks[].clips[].asset.src
3. Загрузка всех видео-файлов через Uploader
4. Замена placeholders на URL через TimelineBuilder
5. Отправка на рендеринг через ShotstackClient
6. Ожидание завершения (polling)
7. Скачивание результата

### 6. Check Module (`fast_clip/check/`)

**Назначение:** Валидация Shotstack-native JSON скриптов перед обработкой.

**Проверки:**
- Существование файлов
- Валидность JSON
- Поддерживаемые transitions, effects, filters
- Корректность aspect_ratio, format, fps
- Валидность длительности клипов

**Поддерживаемые значения:**
- Transitions: fade, fadeFast, slideLeft, slideRight и др.
- Effects: zoomIn, zoomOut, kenBurns
- Filters: boost, greyscale, contrast, muted, negative, darken, lighten
- Aspect Ratios: 9:16, 16:9, 1:1, 4:5, 4:3
- Formats: mp4, mov, webm, gif

## Форматы данных

### Markdown Script Format

```markdown
## name: project_name
## resources_dir: Video_01
## soundtrack: music.mp3
## soundtrack_volume: 0.5
## background: "#000000"

| # | Resource | Trim | Duration | Trans In | Effect | Filter | Trans Out | Volume | Description |
|---|----------|------|----------|----------|--------|--------|-----------|--------|-------------|
| 1 | clip.mp4 | 00:00| 5s       | fadeFast | zoomIn | boost  | slideLeft | 1.0    | Intro       |

## output_format: mp4
## resolution: 1080p
## aspect_ratio: 9:16
## fps: 30
```

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
