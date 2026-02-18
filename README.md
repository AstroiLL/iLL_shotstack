# Fast-Clip

Простой инструмент для создания видео из видео-клипов по скрипту в формате Markdown или Shotstack-native JSON.

## Что делает программа

Fast-Clip позволяет автоматически собирать видео из нескольких клипов с помощью облачного сервиса [Shotstack](https://shotstack.io/). Вы создаете скрипт в Markdown или JSON, который описывает:

- Какие клипы использовать и с какого момента
- Длительность каждого клипа
- Переходы между клипами (fade, slide, zoom и др.)
- Эффекты во время клипа (zoomIn, kenBurns)
- Фильтры цветокоррекции (boost, greyscale)
- Фоновую музыку и общие настройки

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
git clone https://github.com/AstroiLL/iLL_shortstack.git
cd iLL_shortstack
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
./build.sh script_video_04.json

# С подробным выводом
./build.sh -v script_video_04.json

# Указать папку для сохранения
./build.sh -o ./output script_video_04.json
```

### Или через Python

```bash
uv run python assemble.py script_video_04.json -v
```

## Формат скрипта

### Markdown формат (рекомендуется)

Скрипты удобно писать в Markdown с таблицей:

```markdown
## name: my_video
## resources_dir: Video_01
## soundtrack: music.mp3
## soundtrack_volume: 0.5
## background: "#000000"

| # | Resource | Trim | Duration | Trans In | Effect | Filter | Trans Out | Volume | Description |
|---|----------|------|----------|----------|--------|--------|-----------|--------|-------------|
| 1 | clip_01.mp4 | 00:00| 5s       | fadeFast | zoomIn | boost  | slideLeftFast | 1.0 | Intro |
| 2 | clip_02.mp4 | 00:10| 3s       | fade     |        |        | fade      | 0.8 | Middle |

## output_format: mp4
## resolution: 1080p
## aspect_ratio: 9:16
## fps: 30
## thumbnail_capture: 1
```

### Описание полей таблицы

| Поле | Описание | Пример |
|------|----------|--------|
| `#` | Порядковый номер | 1, 2, 3... |
| `Resource` | Имя файла видео или изображения | clip.mp4, photo.jpg |
| `Trim` | Время начала в исходном файле | 00:00, 00:30, 01:15 |
| `Duration` | Длительность клипа | 5s, 10s, 3.5s |
| `Trans In` | Переход на входе | fadeFast, slideLeftFast |
| `Effect` | Эффект во время клипа | zoomIn, kenBurns |
| `Filter` | Цветовой фильтр | boost, greyscale, contrast |
| `Trans Out` | Переход на выходе | fade, zoomFast |
| `Volume` | Громкость клипа (0.0-1.0) | 1.0, 0.5, 0.0 |
| `Description` | Описание (не используется в видео) | Произвольный текст |

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
- `thumbnail_capture` - секунда для thumbnail

### Конвертация MD в JSON

```bash
uv run python convert_script.py script.md
# Создаст script.json с Shotstack-native форматом
```

### Shotstack-native JSON формат

После конвертации получается родной формат Shotstack:

```json
{
  "name": "my_video",
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
          "src": "{{Video_01/clip_01.mp4}}",
          "trim": 0,
          "volume": 1.0
        },
        "start": "auto",
        "length": 5.0,
        "transition": {"in": "fadeFast", "out": "slideLeftFast"},
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
uv run python check.py script_video_04.json -v
```

## Примеры

В репозитории есть примеры скриптов:
- `script_video_04.md` - пример с эффектами и фильтрами
- `script_video_04.json` - результат конвертации в Shotstack формат
- `Video_01/` - папка с тестовыми видео

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

# Проверить версии
uv --version
python --version
```

## Лицензия

MIT
