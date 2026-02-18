# Fast-Clip - Техническое описание проекта

## Обзор

Fast-Clip - Python-приложение для автоматической сборки видео из клипов с использованием Shotstack API. Приложение состоит из модульной архитектуры с четким разделением ответственности.

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
│   ├── timeline_builder.py      # Конвертация скриптов в Shotstack формат
│   ├── shotstack_client.py      # API клиент для рендеринга
│   └── assembler.py             # Главный оркестратор
│
├── assemble.py                  # CLI для сборки видео
├── build.sh                     # Bash скрипт для быстрого запуска
├── check.py                     # Legacy standalone checker
├── convert_script.py            # Конвертер MD/JSON
│
├── .env                         # Конфигурация окружения
├── .env.example                 # Шаблон конфигурации
├── pyproject.toml               # Зависимости проекта
└── uv.lock                      # Lock файл uv
```

### Поток данных

```
JSON Script → Validation → Upload → Timeline Builder → Shotstack API → Download
     ↓            ↓           ↓            ↓               ↓              ↓
  check.py   validator   uploader   timeline_      shotstack      assembler
                                    builder.py     _client.py
```

## Компоненты

### 1. Uploader (`fast_clip/uploader.py`)

**Назначение:** Загрузка локальных видео-файлов в Shotstack через Ingest API.

**Основные методы:**
- `upload(file_path)` - загрузка одного файла с ожиданием обработки
- `_get_signed_url()` - получение signed URL для загрузки
- `_wait_for_file_ready()` - polling статуса обработки (до 60 сек)

**Важно:** Shotstack требует время для обработки загруженных файлов. Метод `_wait_for_file_ready()` делает polling API каждые 2 секунды до получения статуса "ready".

### 2. Timeline Builder (`fast_clip/timeline_builder.py`)

**Назначение:** Конвертация формата скриптов Fast-Clip в формат Shotstack Edit API.

**Ключевые преобразования:**
- `time_start` → `asset.trim` (обрезка начала)
- `time_end - time_start` → `length` (длительность клипа)
- Эффекты (`fade_in`/`fade_out`) → `transition.in`/`transition.out`
- Разрешение + ориентация → `output.size`

**Поддерживаемые эффекты:**
- `fade_in` → `transition: {in: "fade"}`
- `fade_out` → `transition: {out: "fade"}`
- `slide_in`/`slide_out` - заготовлены, требуют доработки

### 3. Shotstack Client (`fast_clip/shotstack_client.py`)

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

### 4. Assembler (`fast_clip/assembler.py`)

**Назначение:** Главный оркестратор, объединяющий все компоненты.

**Процесс сборки:**
1. Загрузка и валидация JSON скрипта
2. Загрузка всех видео-файлов через Uploader
3. Сборка timeline через TimelineBuilder
4. Отправка на рендеринг через ShotstackClient
5. Ожидание завершения (polling)
6. Скачивание результата

### 5. Check Module (`fast_clip/check/`)

**Назначение:** Валидация скриптов перед обработкой.

**Проверки:**
- Существование файлов
- Валидность JSON
- Корректность временных меток
- Поддерживаемые форматы и эффекты
- Наличие обязательных полей

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

**Формат запроса:**
```json
{
  "timeline": {
    "tracks": [{
      "clips": [{
        "asset": {
          "type": "video",
          "src": "https://...",
          "trim": 0
        },
        "start": "auto",
        "length": 5,
        "transition": {"in": "fade"}
      }]
    }]
  },
  "output": {
    "format": "mp4",
    "size": {"width": 1920, "height": 1080}
  }
}
```

## Конфигурация

### Переменные окружения (.env)

```bash
SHOTSTACK_API_KEY=xxx        # Обязательно
SHOTSTACK_ENV=stage          # stage или v1 (production)
```

### Зависимости (pyproject.toml)

```toml
[project]
requires-python = ">=3.13"
dependencies = [
    "pydantic",        # Валидация данных
    "requests",        # HTTP клиент
    "python-dotenv",   # Загрузка .env
]
```

## Разработка

### Установка dev-зависимостей

```bash
uv add --dev ruff mypy
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

# Тестирование (ручное)
uv run python assemble.py script_video_01.json -v
```

## Расширение функциональности

### Добавление нового эффекта

1. Добавить в `EFFECT_MAP` в `timeline_builder.py`:
```python
"zoom_in": {"effect": "zoomIn"}
```

2. Добавить валидацию в `fast_clip/check/validator.py`:
```python
VALID_EFFECTS = {"fade_in", "fade_out", "zoom_in"}
```

3. Обновить документацию в README.md

### Поддержка нового типа ассета

1. Расширить `_build_clip()` в `timeline_builder.py`
2. Добавить тип в `parse_timeline_item()` в `validator.py`
3. Обновить схему в `convert_script.py` (Pydantic модели)

## Известные ограничения

- Максимум 10 клипов в timeline (ограничение валидатора)
- Только fade эффекты реализованы полностью
- Нет поддержки аудио дорожек
- Требуется интернет-соединение для работы с API
- На бесплатном тарифе Shotstack есть ограничения

## Отладка

### Включение verbose режима

```bash
uv run python assemble.py script.json -v
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

## Контакты и ресурсы

- Shotstack Docs: https://shotstack.io/docs/api/
- API Reference: https://shotstack.io/docs/api/api
- Python версия: 3.13+
- Менеджер пакетов: uv
