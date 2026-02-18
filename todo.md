# TODO

## ✅ Готово

### MVP Video Assembler
1. ✅ Исследован Shotstack Ingest API
2. ✅ Модуль загрузки (`fast_clip/uploader.py`) с ожиданием обработки
3. ✅ Timeline Builder (`fast_clip/timeline_builder.py`)
4. ✅ Shotstack Client (`fast_clip/shotstack_client.py`)
5. ✅ Video Assembler (`fast_clip/assembler.py`)
6. ✅ CLI (`assemble.py`)
7. ✅ **Протестировано с реальным API** - видео успешно собрано!

### Переход на Shotstack-native формат ✅
1. ✅ Обновлен `convert_script.py` - MD → Shotstack JSON напрямую
2. ✅ Новая структура таблицы Markdown (Trim, Duration, Trans In/Out, Effect, Filter, Volume)
3. ✅ Поддержка всех Shotstack transitions (fadeFast, slideLeftFast и др.)
4. ✅ Поддержка effects (zoomIn, zoomOut, kenBurns)
5. ✅ Поддержка filters (boost, greyscale, contrast, muted, negative)
6. ✅ Поддержка soundtrack и background
7. ✅ Обновлен `check.py` для валидации Shotstack-native JSON
8. ✅ Обновлен `timeline_builder.py` - замена placeholders на URL
9. ✅ Обновлен `assembler.py` - работа с новым форматом
10. ✅ Обновлена документация (README.md, PROJECT.md)

### Результат теста
```bash
$ uv run python assemble.py script_video_04.json -v
🎬 Fast-Clip Video Assembler
📤 Uploading video files...
   [1/2] Uploading clip_01.mp4... ✓
   [2/2] Uploading clip_02.mp4... ✓
🎬 Building timeline...
🚀 Submitting render job...
⏳ Waiting for render to complete...
   Status: fetching → rendering → done
💾 Downloading video...
✅ Assembly complete!

Output: video_res_01.mp4 (8.2MB)
Render ID: 82b03369-bc77-4ccf-81e3-e55292a5abe1
```

## 🔄 Следующие шаги (опционально)

### Улучшения
- [ ] Добавить еще больше эффектов (crop, rotate)
- [ ] Поддержка текстовых наложений (titles)
- [ ] Progress bar (tqdm) для загрузки/рендеринга
- [ ] Batch processing (несколько скриптов)
- [ ] Шаблоны для типовых видео
- [ ] Кэширование загруженных файлов
- [ ] Превью кадра перед сборкой

### Тестирование и документация
- [ ] Unit тесты для модулей
- [ ] Integration тесты
- [ ] Документация по API

### DevOps
- [ ] CI/CD pipeline
- [ ] Docker контейнер
- [ ] Pre-commit hooks (ruff, mypy)

## 📚 Использование

```bash
# Установка зависимостей
uv sync

# Настройка API ключа (уже настроено в .env)
export SHOTSTACK_API_KEY=your_key

# Конвертация MD в JSON
uv run python convert_script.py script_video_04.md

# Проверка скрипта
uv run python check.py script_video_04.json -v

# Сборка видео
uv run python assemble.py script_video_04.json -v
```

## 📁 Структура проекта

```
fast_clip/
├── __init__.py
├── check/              # Валидация скриптов (Shotstack-native JSON)
├── uploader.py         # Загрузка в Shotstack
├── timeline_builder.py # Замена {{}} placeholders на URL
├── shotstack_client.py # API клиент
└── assembler.py        # Главный оркестратор

convert_script.py       # MD → Shotstack JSON
assemble.py             # CLI для сборки
check.py                # Валидатор Shotstack JSON
.env                    # Конфигурация API ключей
```

## ✨ Функции

- ✅ Загрузка локальных видео в Shotstack
- ✅ Поддержка всех Shotstack transitions
- ✅ Поддержка effects: zoomIn, zoomOut, kenBurns
- ✅ Поддержка filters: boost, greyscale, contrast, muted, negative
- ✅ Фоновая музыка (soundtrack)
- ✅ Цвет фона (background)
- ✅ Aspect ratio (9:16, 16:9, 1:1, 4:5, 4:3)
- ✅ Индивидуальная громкость для каждого клипа
- ✅ Shotstack-native JSON формат
- ✅ Markdown формат с таблицей
- ✅ Валидация скриптов перед сборкой
- ✅ Автоматическое ожидание рендеринга
- ✅ Скачивание готового видео
