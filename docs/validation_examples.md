# Fast-Clip Validation Examples

Примеры использования новой системы валидации Fast-Clip.

## Базовая валидация

### Простая проверка
```bash
# Проверить скрипт с базовыми настройками
uv run python check.py script.json

# Проверить с детальным выводом
uv run python check.py -v script.json

# Тихая проверка (только код возврата)
uv run python check.py -q script.json && echo "OK"
```

### Строгая валидация
```bash
# Все предупреждения считаются ошибками
uv run python check.py --strict script.json

# Пропуск валидации (не рекомендуется)
uv run python check.py --skip-validate script.json
```

## Интеграция в рабочий процесс

### Конвертация с валидацией
```bash
# Конвертировать MD в JSON с валидацией
uv run python convert_script.py --validate script.md

# Конвертировать со строгой валидацией
uv run python convert_script.py --strict --validate script.md

# Проверить результат валидации
if uv run python convert_script.py --validate script.md; then
    echo "Конвертация прошла успешно!"
else
    echo "Обнаружены ошибки валидации"
fi
```

### Сборка видео с валидацией
```bash
# Стандартная сборка с валидацией
uv run python assemble.py script.json

# Сборка без валидации (быстрый режим)
uv run python assemble.py --skip-validate script.json

# Сборка со строгой валидацией
uv run python assemble.py --strict script.json
```

## Примеры скриптов

### Валидный скрипт
```json
{
  "template": {
    "timeline": {
      "tracks": [
        {
          "clips": [
            {
              "asset": {
                "type": "video",
                "src": "{{intro.mp4}}"
              },
              "start": 0.0,
              "length": 3.0,
              "transition": {
                "in": "fade"
              }
            },
            {
              "asset": {
                "type": "video", 
                "src": "{{main_content.mp4}}"
              },
              "start": 3.0,
              "length": 10.0,
              "effect": "kenBurns"
            }
          ]
        }
      ]
    }
  },
  "output": {
    "format": "mp4",
    "aspectRatio": "16:9"
  },
  "merge": [
    {"find": "intro.mp4", "replace": "https://example.com/intro.mp4"},
    {"find": "main_content.mp4", "replace": "https://example.com/content.mp4"}
  ]
}
```

### Скрипт с предупреждениями
```json
{
  "template": {
    "timeline": {
      "tracks": [
        {
          "clips": [
            {
              "asset": {
                "type": "video",
                "src": "{{video.mp4}}"
              },
              "start": 0.0,
              "length": 5.0,
              "transition": {
                "in": "invalidTransition"  // Предупреждение: неизвестный transition
              }
            }
          ]
        }
      ]
    }
  },
  "output": {
    "format": "mp4"
  },
  "merge": [
    {"find": "video.mp4", "replace": ""}
  ]
}
```

### Сложный скрипт
```json
{
  "template": {
    "timeline": {
      "tracks": [
        {
          "clips": [
            {
              "asset": {
                "type": "video",
                "src": "{{intro.mp4}}"
              },
              "start": 0.0,
              "length": 2.0,
              "transition": {
                "in": "fadeFast",
                "out": "slideLeft"
              }
            }
          ]
        },
        {
          "clips": [
            {
              "asset": {
                "type": "video",
                "src": "{{main_video.mp4}}"
              },
              "start": 2.0,
              "length": 8.0,
              "effect": "zoomIn",
              "filter": "contrast"
            }
          ]
        },
        {
          "clips": [
            {
              "asset": {
                "type": "image",
                "src": "{{title.png}}"
              },
              "start": 10.0,
              "length": 3.0,
              "transition": {
                "in": "reveal"
              }
            }
          ]
        },
        {
          "clips": [
            {
              "asset": {
                "type": "audio",
                "src": "{{background_music.mp3}}"
              },
              "start": 0.0,
              "length": 13.0
            }
          ]
        }
      ]
    }
  },
  "output": {
    "format": "mp4",
    "aspectRatio": "16:9",
    "fps": 30.0
  },
  "merge": [
    {"find": "intro.mp4", "replace": "https://example.com/intro.mp4"},
    {"find": "main_video.mp4", "replace": "https://example.com/main.mp4"},
    {"find": "title.png", "replace": "https://example.com/title.png"},
    {"find": "background_music.mp3", "replace": "https://example.com/music.mp3"}
  ]
}
```

## Лучшие практики

### 1. Структура проекта
```
my_project/
├── script.md              # Основной скрипт
├── Content/              # Медиафайлы
│   ├── intro.mp4
│   ├── main_video.mp4
│   └── background_music.mp3
├── output/               # Результаты сборки
└── .env                 # Конфигурация
```

### 2. Именование файлов
- Используйте понятные имена: `intro.mp4`, `main_content.mp4`, `background_music.mp3`
- Избегайте пробелы и специальные символы
- Используйте нижний регистр с подчеркиваниями

### 3. Проверка перед сборкой
```bash
# Всегда проверяйте скрипты перед сборкой
uv run python check.py script.json

# Интегрируйте в автоматические скрипты
if uv run python check.py -q script.json; then
    echo "Начинаю сборку..."
    uv run python assemble.py script.json
else
    echo "Найдены ошибки, исправьте их сначала"
    exit 1
fi
```

### 4. Валидация файлов
- Проверяйте наличие всех файлов перед сборкой
- Используйте относительные пути
- Убедитесь в правах доступа к файлам

### 5. Оптимизация
```bash
# Для больших проектов используйте строгую валидацию
uv run python check.py --strict complex_script.json

# Пропускайте валидацию для быстрых тестов
uv run python assemble.py --skip-validate test_script.json
```

### 6. Отладка
```bash
# Используйте verbose режим для детальной информации
uv run python assemble.py -v script.json

# Проверяйте результаты валидации
uv run python check.py -v script.json | head -20
```

### 7. Автоматизация
```bash
#!/bin/bash
# auto_build.sh - автоматическая сборка с валидацией

for script in scripts/*.json; do
    echo "Проверяю: $script"
    if uv run python check.py -q "$script"; then
        echo "Собираю: $script"
        uv run python assemble.py "$script"
        echo "Готово: $script"
    else
        echo "Ошибки в: $script"
    fi
done
```

## Обработка ошибок

### Типичные ошибки и решения

1. **Отсутствующие файлы**
   - Ошибка: `Media file not found: '{{video.mp4}}'`
   - Решение: Убедитесь что файлы существуют в директории Content/

2. **Неверные transitions**
   - Ошибка: `Unknown transition: 'invalidTransition'`
   - Решение: Используйте только валидные значения: fade, slideLeft, zoom и др.

3. **Проблемы с JSON синтаксисом**
   - Ошибка: `Invalid JSON: Expecting ',' delimiter`
   - Решение: Проверьте синтаксис JSON, особенно запятые и скобки

4. **Отсутствующие merge entries**
   - Ошибка: `Placeholder 'video.mp4' has no matching merge entry`
   - Решение: Добавьте соответствующую запись в массив merge

## Интеграция с CI/CD

### GitHub Actions
```yaml
name: Validate and Build
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.13'
    - name: Install dependencies
      run: |
        pip install uv
        uv sync
    - name: Validate scripts
      run: |
        for script in scripts/*.json; do
          uv run python check.py "$script" || exit 1
        done
```

## Профилирование производительности

### Измерение времени валидации
```bash
# Измерение времени валидации
time uv run python check.py -v script.json

# Профилирование Python
python -m cProfile -o profile.stats uv run python check.py script.json
```

Эта документация поможет пользователям эффективно использовать систему валидации и интегрировать ее в свои рабочие процессы.