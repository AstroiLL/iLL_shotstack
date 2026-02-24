# Shotstack API Service

## Описание

[Shotstack](https://shotstack.io/) - облачный сервис для автоматической сборки и рендеринга видео через API.

## API Endpoints

### Ingest API (Загрузка файлов)
- **Base URL:** `https://api.shotstack.io/ingest/stage`
- POST `/upload` - получение signed URL для загрузки
- PUT `<signed_url>` - загрузка файла
- GET `/sources/{id}` - проверка статуса обработки

### Edit API (Рендеринг видео)
- **Base URL:** `https://api.shotstack.io/edit/stage`
- POST `/render` - отправка задания на рендеринг
- GET `/render/{id}` - проверка статуса рендеринга

## Документация

- **API Docs:** https://shotstack.io/docs/api/
- **API Reference:** https://shotstack.io/docs/api/api
- **Dashboard:** https://dashboard.shotstack.io/

## Тарифы

- **Free:** Бесплатный тариф с ограничениями
- **Pro:** Платные тарифы для production

## Форматы и возможности

### Поддерживаемые видео форматы
- mp4, mov, avi, mkv (вход)
- mp4, mov, webm, gif (выход)

### Поддерживаемые изображения
- jpg, png

### Переходы (Transitions)
fade, fadeFast, fadeSlow, slideLeft, slideRight, slideUp, slideDown, slideLeftFast, slideRightFast, wipeLeft, wipeRight, zoom, zoomFast, carouselLeft, carouselRight, reveal, shuffleTopRight и др.

### Эффекты (Effects)
zoomIn, zoomOut, kenBurns

### Фильтры (Filters)
boost, greyscale, contrast, muted, negative, darken, lighten

## Статусы рендеринга

- `queued` - в очереди
- `fetching` - загрузка ассетов
- `rendering` - рендеринг
- `done` - готово
- `failed` - ошибка

## Инструменты командной строки

### convert_script.py

Конвертер между форматами MD и Shotstack JSON.

**Режимы вывода:**
- `convert_script.py script.md` - обычный режим (только результат)
- `convert_script.py -v script.md` - подробный вывод (парсинг, клипы, merge поля)
- `convert_script.py -q script.md` - без вывода (только код возврата)

### check.py

Валидатор Shotstack JSON скриптов.

**Режимы вывода:**
- `check.py script.json` - обычная проверка (ошибки и предупреждения)
- `check.py -v script.json` - подробная проверка (все детали валидации)
- `check.py -q script.json` - тихий режим (только код возврата 0/1)

### assemble.py

Сборка видео через Shotstack API.

**Параметры:**
- `assemble.py script.json` - сборка с базовым выводом
- `assemble.py -v script.json` - подробный вывод процесса
- `assemble.py -o ./output script.json` - указать папку для сохранения

## Получение API ключа

1. Зарегистрируйтесь на https://shotstack.io/
2. Перейдите в Dashboard
3. Скопируйте API ключ для Stage (тестовый) или Production
