# Fast-Clip

Простой инструмент для создания видео из видео-клипов по скрипту в формате Markdown или Shotstack-native JSON.

## Что делает программа

Fast-Clip позволяет автоматически собирать видео из нескольких клипов с помощью облачного сервиса [Shotstack](https://shotstack.io/). Вы создаете скрипт в Markdown, который описывает:

- Видео-клипы и звуковые эффекты
- Длительность каждого клипа
- Переходы между клипами (fade, slide, zoom и др.)
- Эффекты во время клипа (zoomIn, kenBurns)
- Фоновую музыку и общие настройки

Программа автоматически:
1. Конвертирует MD скрипт в Shotstack template формат
2. Загружает клипы в облако Shotstack
3. Собирает видео со звуковыми эффектами
4. Скачивает готовое видео

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

## Использование

### Быстрый старт

```bash
# Конвертировать MD в JSON (автоопределение формата)
uv run python convert_script.py script.md

# Собрать видео из скрипта
./build.sh script.json

# С подробным выводом
./build.sh -v script.json

# Указать папку для сохранения
./build.sh -o ./output script.json
```

### Или через Python

```bash
# Конвертация (автоопределение направления)
uv run python convert_script.py script.md        # MD -> JSON
uv run python convert_script.py script.json      # JSON -> MD

# Сборка видео
uv run python assemble.py script.json -v
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
|---|------|-------------|------|--------|----------|--------|--------------|--------------|
| 1 | Привет! | Аватар | avatar.mp4 | 00:00:000-00:03:000 | 3.0s | ZoomIn | | |
| 2 | Как дела? | Аватар | avatar.mp4 | 00:03:000-00:05:500 | 2.5s | | | click.wav |
| 3 | Смотри это | Видео | content.mp4 | 00:05:500-00:08:000 | 2.5s | | | whoosh.wav |

## output_format: mp4
## resolution: 1080p
## aspect_ratio: 9:16
## fps: 30
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

### Конвертация форматов

```bash
# MD -> JSON (автоопределение)
uv run python convert_script.py script.md
# Создаст script.json с Shotstack template форматом

# JSON -> MD (автоопределение)
uv run python convert_script.py script.json
# Создаст script.md из JSON

# При существовании файла добавляется индекс:
# script.json -> script_1.json -> script_2.json
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
      "background": "#000000",
      "tracks": [{
        "clips": [{
          "asset": {
            "type": "video",
            "src": "{{Content/avatar.mp4}}",
            "trim": 0
          },
          "start": 0.0,
          "length": 3.0,
          "transition": {"in": "zoom"},
          "effect": "zoomIn"
        }]
      }, {
        "clips": [{
          "asset": {
            "type": "audio",
            "src": "{{Content/click.wav}}"
          },
          "start": 3.0,
          "length": 2.5
        }]
      }]
    },
    "output": {
      "format": "mp4",
      "resolution": "1080p",
      "aspectRatio": "9:16",
      "fps": 30
    }
  },
  "merge": [
    {"find": "Content/avatar.mp4", "replace": ""},
    {"find": "Content/click.wav", "replace": ""}
  ]
}
```

## Поддерживаемые эффекты

### Переходы (Transitions)

| Категория | Доступные значения |
|-----------|-------------------|
| Fade | fade, fadeFast, fadeSlow |
| Slide | slideLeft, slideRight, slideUp, slideDown, slideLeftFast, slideRightFast |
| Wipe | wipeLeft, wipeRight, wipeLeftFast, wipeRightFast |
| Carousel | carouselLeft, carouselRight, carouselUpFast |
| Reveal | reveal, revealFast, revealSlow |
| Zoom | zoom, zoomFast, zoomSlow |
| Shuffle | shuffleTopRight, shuffleLeftBottom |

### Эффекты (Effects)

- `zoomIn` - плавное приближение
- `zoomOut` - плавное отдаление
- `kenBurns` - панорама + зум

### Фильтры (Filters)

- `boost` - контраст + насыщенность
- `greyscale` - черно-белый
- `contrast` - повышенный контраст
- `muted` - приглушенные тона
- `negative` - негатив
- `darken` / `lighten` - яркость

## Проверка скрипта

Перед сборкой проверьте скрипт на ошибки:

```bash
uv run python check.py script.json -v
```

## Примеры

В репозитории есть примеры скриптов:
- `script_content.md` - пример с текстовыми оверлеями и звуковыми эффектами
- `test_script.md` - простой тестовый пример
- `Content/` - папка с тестовыми видео

## Особенности

### Гибридный подход Template + Merge

Fast-Clip использует оптимальный подход:
1. **Template** - структура видео с плейсхолдерами {{file}}
2. **Merge** - замена плейсхолдеров на реальные URL после загрузки
3. **Авто-индексация** - при существовании файла создается новый с индексом

### Двусторонняя конвертация

- **MD → JSON**: Создает Shotstack template с текстовыми оверлеями
- **JSON → MD**: Восстанавливает MD таблицу из template

## Ограничения

- Максимум 10 клипов в одном видео
- Исходные видео должны быть в папке `resources_dir`
- Поддерживаемые форматы: mp4, mov, avi, mkv для видео; jpg, png для изображений
- На бесплатном тарифе Shotstack есть ограничения на длительность и количество рендеров

## Получение помощи

```bash
# Справка по использованию
./build.sh --help
uv run python assemble.py --help
uv run python convert_script.py --help

# Проверить версии
uv --version
python --version
```

## Лицензия

MIT
