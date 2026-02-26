# Fast-Clip

Простой инструмент для создания видео из видео-клипов по скрипту в формате Markdown или Shotstack-native JSON с комплексной валидацией.

## Что делает программа

Fast-Clip позволяет автоматически собирать видео из нескольких клипов с помощью облачного сервиса [Shotstack](https://shotstack.io/). Вы создаете скрипт в Markdown, который описывает:

- Видео-клипы и звуковые эффекты
- Длительность каждого клипа
- Переходы между клипами (fade, slide, zoom и др.)
- Эффекты во время клипа (zoomIn, kenBurns)
- Фоновую музыку и общие настройки

Программа автоматически:
1. Конвертирует MD скрипт в Shotstack template формат с опциональной валидацией
2. Валидирует JSON структуру и содержимое с подробными ошибками
3. Загружает клипы в облако Shotstack
4. Собирает видео со звуковыми эффектами
5. Скачивает готовое видео

### ⚠️ Важные ограничения

- **Текстовые оверлеи**: В текущей версии не поддерживаются (требуется реализация отдельных title клипов)
- **Thumbnail**: Параметр `thumbnail_capture` временно отключен (вызывает ошибку валидации Shotstack API)

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
git clone https://github.com/AstroiLL/iLL_shotstack.git
cd iLL_shotstack
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

## Валидация и интеграция

Fast-Clip включает комплексную систему валидации:

### Типы проверок

1. **JSON структура**: Проверка синтаксиса и обязательных полей
2. **Доступность файлов**: Проверка существования медиафайлов
3. **Соответствие API**: Валидация полей согласно Shotstack спецификациям

### Уровни ошибок

- **ERROR**: Критические ошибки, блокирующие выполнение
- **WARNING**: Рекомендации, не блокирующие выполнение

### Интеграция в рабочий процесс

```bash
# Автоматическая валидация в конвертере
uv run python convert_script.py --validate script.md

# Валидация перед сборкой
uv run python assemble.py script.json  # По умолчанию
uv run python assemble.py --skip-validate script.json  # Пропуск проверки
```

## Использование

### Быстрый старт

```bash
# Конвертировать MD в JSON (автоопределение формата)
uv run python convert_script.py script.md

# Конвертация с подробным выводом
uv run python convert_script.py -v script.md

# Конвертация без вывода (только код возврата)
uv run python convert_script.py -q script.md

# Собрать видео из скрипта
./build.sh script.json

# С подробным выводом
./build.sh -v script.json

# Указать папку для сохранения
./build.sh -o ./output script.json
```

### Валидация скриптов

Fast-Clip включает комплексную систему валидации:

```bash
# Базовая валидация
uv run python check.py script.json              # Проверка с рекомендациями
uv run python check.py -v script.json           # Проверка с деталями
uv run python check.py -q script.json           # Проверка без вывода (только код возврата)

# Строгая валидация (warnings как ошибки)
uv run python check.py --strict script.json

# Пропуск валидации (не рекомендуется)
uv run python check.py --skip-validate script.json
```

### Интеграция валидации

Валидация автоматически интегрирована в рабочий процесс:

```bash
# Конвертация с валидацией
uv run python convert_script.py --validate script.md

# Сборка с валидацией (по умолчанию)
uv run python assemble.py script.json

# Сборка без валидации (быстрый режим)
uv run python assemble.py --skip-validate script.json

# Сборка со строгой валидацией
uv run python assemble.py --strict script.json
```

### Или через Python

```bash
# Конвертация (автоопределение направления)
uv run python convert_script.py script.md              # MD -> JSON (normal mode)
uv run python convert_script.py -v script.md           # MD -> JSON (verbose mode)
uv run python convert_script.py -q script.md           # MD -> JSON (quiet mode)
uv run python convert_script.py script.json            # JSON -> MD

# Конвертация с валидацией
uv run python convert_script.py --validate script.md
uv run python convert_script.py --strict --validate script.md

# Сборка видео
uv run python assemble.py script.json -v
```

### Режимы вывода

Инструменты поддерживают три режима вывода:

- **Normal** (по умолчанию): показывает только основную информацию (имя проекта, ресурсы, количество клипов)
- **Verbose** (`-v`, `--verbose`): детальный построчный вывод всех операций (парсинг, создание клипов, merge поля)
- **Quiet** (`-q`, `--quiet`): полное отключение вывода, только код возврата (0 = успех, 1 = ошибка)

Режим quiet полезен для автоматизации и скриптов:

```bash
# Проверка в скрипте
if uv run python check.py -q script.json; then
    echo "Скрипт валиден, запускаем сборку..."
    ./build.sh script.json
else
    echo "Ошибка валидации!"
    exit 1
fi
```

## Формат скрипта

### Markdown формат (рекомендуется)

Скрипты удобно писать в Markdown с таблицей:

```markdown
## name: my_video
## resources_dir: Content
## soundtrack: music.mp3
## soundtrack_volume: 0.5
## background: "#000000"

| # | Text | Description | Clip | Timing | Duration | Effect | Music effect | Sound effect |
|---|------|-------------|--------|--------|----------|--------|--------------|--------------|
| 1 | Привет! | Аватар | avatar.mp4 | 00:00:000-00:03:000 | 3.0s | ZoomIn | | |
| 2 | Как дела? | Аватар | avatar.mp4 | 00:03:000-00:05:500 | 2.5s | | | click.wav |
| 3 | Смотри это | Видео | content.mp4 | 00:05:500-00:08:000 | 2.5s | | | whoosh.wav |

## output_format: mp4
## resolution: 1080p
## aspect_ratio: 9:16
## fps: 30
```

### Shotstack Template JSON формат

После конвертации получается template формат Shotstack с merge полями:

```json
{
  "name": "my_video",
  "resourcesDir": "Content",
  "template": {
    "timeline": {
      "soundtrack": {
        "src": "{{Content/music.mp3}}",
        "effect": "fadeIn",
        "volume": 0.5
      },
      "tracks": [
        {
          "clips": [
            {
              "asset": {
                "type": "video",
                "src": "{{Content/video.mp4}}"
              },
              "start": 0.0,
              "length": 5.0,
              "transition": {
                "in": "fade",
                "out": "slideLeft"
              },
              "effect": "zoomIn"
            }
          ]
        }
      ]
    }
  },
  "output": {
    "format": "mp4",
    "aspectRatio": "9:16",
    "resolution": "hd",
    "fps": 30
  },
  "merge": [
    {"find": "Content/video.mp4", "replace": ""},
    {"find": "Content/music.mp3", "replace": ""}
  ]
}
```

### Описание полей таблицы

| Поле | Описание | Пример |
|------|----------|--------|
| `#` | Порядковый номер | 1, 2, 3... |
| `Text` | Текст (сохраняется в скрипте, не отображается в видео) | "Привет!", "Смотри" |
| `Description` | Описание сцены (не в видео) | Аватар, Видео |
| `Clip` | Имя файла видео | avatar.mp4, content.mp4 |
| `Timing` | Временной интервал | 00:00:000-00:03:000 |
| `Duration` | Длительность клипа | 3.0s, 2.5s |
| `Effect` | Визуальный эффект | ZoomIn, FadeIn, FadeOut |
| `Music effect` | Эффект для фоновой музыки | FadeIn, FadeOut |
| `Sound effect` | Звуковой эффект | click.wav, whoosh.wav |

### Заголовки скрипта

- `name` - название проекта
- `resources_dir` - папка с исходными файлами
- `soundtrack` - фоновая музыка (опционально)
- `soundtrack_volume` - громкость музыки (0.0-1.0)
- `background` - цвет фона (#000000)
- `output_format` - формат выходного файла (mp4, mov, webm, gif)
- `resolution` - разрешение (2160p, 1440p, 1080p, 720p, 480p)
- `aspect_ratio` - соотношение сторон (9:16, 16:9, 1:1, 4:5, 4:3)
- `fps` - кадров в секунду

## Build, Lint, and Test Commands

```bash
# Install/sync dependencies
uv sync

# Convert between formats (auto-detection by file extension)
uv run python convert_script.py script.md              # MD -> JSON (normal mode)
uv run python convert_script.py -v script.md           # MD -> JSON (verbose mode)
uv run python convert_script.py -q script.md           # MD -> JSON (quiet mode)
uv run python convert_script.py script.json            # JSON -> MD
uv run python convert_script.py script.md out.json     # Custom output

# Convert with validation
uv run python convert_script.py --validate script.md     # MD -> JSON with validation
uv run python convert_script.py --strict --validate script.md  # MD -> JSON with strict validation

# Validate Shotstack template JSON
uv run python check.py script.json              # Validate script
uv run python check.py -v script.json           # Verbose validation
uv run python check.py -q script.json           # Quiet validation (exit code only)
uv run python check.py --strict script.json       # Strict validation (warnings as errors)
uv run python check.py --skip-validate script.json  # Skip validation (not recommended)

# Assemble video (needs SHOTSTACK_API_KEY in .env)
uv run python assemble.py script.json                    # Assemble video with validation (default)
uv run python assemble.py script.json -v                 # Verbose mode
uv run python assemble.py script.json -o ./out           # Custom output directory
uv run python assemble.py script.json -o ./out/video.mp4 # Custom output file
uv run python assemble.py --skip-validate script.json  # Skip validation (fast mode)
uv run python assemble.py --strict script.json        # Strict validation

# Check script validation (from any directory)
uv run python check.py MyProject/script.json        # Validate (uses MyProject/Content/ for resources)
cd MyProject && uv run python check.py script.json  # Same, from project directory

# Quick build using shell script
./build.sh script.json                          # Quick build
./build.sh -v script.json                       # Verbose
./build.sh -o ./output script.json              # Custom output

# Type checking
uv run mypy .                                   # Check all files
uv run mypy convert_script.py                   # Check single file

# Linting and formatting
uv run ruff check .                             # Lint all files
uv run ruff check --fix .                       # Auto-fix issues
uv run ruff format .                            # Format all files

# Run individual Python files
uv run python convert_script.py script.md       # Run converter
uv run python check.py script.json              # Run validator
uv run python assemble.py script.json              # Run assembler

# Run tests
uv run python tests/test_validation.py          # Run unit tests
uv run python tests/test_integration.py        # Run integration tests
```

## Project Overview

Fast-Clip is a Python console utility for assembling video projects from fragments using the Shotstack API with template + merge workflow and **comprehensive validation**.

**Workflow:**
1. Create script in Markdown format with table-based timeline (Text, Description, Clip, Sound effect columns)
2. Convert MD to Shotstack Template JSON using `convert_script.py` with optional validation
3. Validate JSON structure and content using `check.py` with comprehensive error reporting
4. Assemble video using `assemble.py` with pre-assembly validation (uploads files via Ingest API, merges URLs, renders, downloads)

**Key Features:**
- **Template + Merge workflow**: JSON contains template structure with `{{file}}` placeholders and merge array
- **Bidirectional conversion**: MD ↔ JSON with auto-detection by file extension
- **File indexing**: Automatic index addition when output file exists (script.json → script_1.json → script_2.json)
- **Text overlays**: Support for text overlays on video clips
- **Sound effects**: Separate audio track for sound effects synchronized with video timing
- **Comprehensive validation**: Multi-level validation system checking JSON structure, file availability, and API compliance

**Validation System:**
- **JSON structure validation**: Syntax, required fields, timeline/track/clip structure
- **File accessibility**: Local file existence and permissions checking
- **API compliance**: Shotstack field validation (transitions, effects, filters, aspect ratios)
- **Error levels**: ERROR (blocking) and WARNING (recommendations) with clear messages

**Key Components:**
- `convert_script.py` - Bidirectional converter (MD ↔ Shotstack Template JSON) with auto-detection and validation
- `check.py` - Comprehensive JSON validation with detailed error reporting and suggestions
- `assemble.py` - Video assembly orchestrator CLI with pre-assembly validation and template + merge support
- `fast_clip/check/validation/` - Modular validation framework (JsonValidator, FileChecker, FieldValidator)
- `fast_clip/uploader.py` - Shotstack file upload (Ingest API)
- `fast_clip/timeline_builder.py` - Replaces `{{placeholders}}` with URLs from merge data
- `fast_clip/shotstack_client.py` - Shotstack Edit API client
- `fast_clip/assembler.py` - Main assembly orchestrator with template workflow

## Supported Shotstack Features

### Transitions (trans_in, trans_out)
fade, fadeFast, fadeSlow, slideLeft, slideRight, slideUp, slideDown, slideLeftFast, slideRightFast, wipeLeft, wipeRight, wipeLeftFast, wipeRightFast, carouselLeft, carouselRight, carouselUpFast, shuffleTopRight, shuffleLeftBottom, reveal, revealFast, revealSlow, zoom, zoomFast, zoomSlow

### Effects
effect: zoomIn, zoomOut, kenBurns

### Filters
filter: boost, greyscale, contrast, muted, negative, darken, lighten

### Aspect Ratios
aspect_ratio: 9:16, 16:9, 1:1, 4:5, 4:3