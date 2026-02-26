## Context

Текущая реализация имеет следующие проблемы:

1. **Валидация ресурсов**: `check.py` ищет файлы относительно текущей рабочей директории, а не относительно JSON файла. При запуске из корня проекта `./check.sh Content/script.json` валидатор ищет файлы в `.` вместо `Content/`.

2. **Отсутствие workspace структуры**: Все файлы (скрипты, медиа, выходные) смешаны в одной директории или разбросаны по проекту.

3. **Выходные файлы**: `assemble.py` не имеет стандартной логики для выходной директории и имени файла.

## Goals / Non-Goals

**Goals:**
1. Исправить валидацию ресурсов - искать файлы относительно директории JSON файла
2. Поддержать workspace структуру с изоляцией проектов
3. Реализовать дефолтную выходную директорию `output/` с именем файла из скрипта
4. Автоматическая индексация выходных файлов (не перезаписывать)
5. CLI флаг `-o, --output` для кастомного пути

**Non-Goals:**
- Изменение формата JSON скрипта
- Изменение Shotstack API интеграции
- Поддержка multiple resources directories
- Автоматическое создание структуры проекта

## Decisions

### Decision 1: Base Path for Resource Validation
**Choice:** Использовать директорию JSON файла как базовый путь для валидации ресурсов.

**Rationale:**
- Естественное поведение - ресурсы относятся к проекту, а проект определяется JSON файлом
- Работает независимо от текущей рабочей директории
- Совместимо с запуском из любого места

**Implementation:**
```python
script_dir = Path(script_path).parent
resources_path = script_dir / resources_dir
```

**Alternatives considered:**
- Использовать `cwd` - отклонено, ломается при запуске из другой директории
- Использовать `resourcesDir` как абсолютный путь - отклонено, не гибко

### Decision 2: Output Directory Structure
**Choice:** По умолчанию использовать `output/` в директории JSON файла.

**Rationale:**
- Стандартная практика для сборочных инструментов
- Отделение входных файлов от выходных
- Легко игнорировать в `.gitignore`

**Implementation:**
```python
output_dir = script_dir / "output"
output_file = output_dir / f"{script_name}.mp4"
```

### Decision 3: File Naming Priority
**Choice:** Использовать `name` из JSON, fallback на имя файла скрипта.

**Rationale:**
- `name` более читаемое и описательное
- Имя файла - надежный fallback

**Priority:**
1. `json_data.get("name")`
2. `script_path.stem`

### Decision 4: Indexing Strategy
**Choice:** Использовать простой инкремент (`_1`, `_2`, `_3`).

**Rationale:**
- Простота реализации
- Предсказуемое поведение
- Не перезаписывает существующие файлы

**Implementation:**
```python
counter = 1
while output_file.exists():
    output_file = output_dir / f"{base_name}_{counter}{ext}"
    counter += 1
```

### Decision 5: CLI Interface for Output
**Choice:** Флаг `-o, --output` поддерживает как директорию, так и полный путь.

**Rationale:**
- Гибкость для пользователя
- Если указана директория - использовать стандартное имя файла
- Если указан файл - использовать его как есть

**Logic:**
```python
if output_path.is_dir():
    final_output = output_path / f"{name}.mp4"
else:
    final_output = output_path
```

## Risks / Trade-offs

**[Risk]** Изменение поведения валидации может сломать существующие workflow → **Mitigation:** Добавить fallback на старое поведение через флаг или переменную окружения

**[Risk]** Создание `output/` может конфликтовать с существующими папками → **Mitigation:** Проверять существование, не перезаписывать содержимое

**[Risk]** Автоматическая индексация может создать много файлов → **Mitigation:** Это ожидаемое поведение, пользователь сам контролирует

**[Trade-off]** Использование `name` из JSON может быть не уникальным → **Acceptance:** Риск низкий, можно переименовать скрипт

## Migration Plan

1. **Phase 1: Fix check.py**
   - Обновить `check_resources()` для использования директории JSON файла
   - Обновить `check_json.py` для передачи правильного пути

2. **Phase 2: Update assemble.py**
   - Добавить парсинг `-o, --output` флага
   - Реализовать логику дефолтного выхода
   - Добавить индексацию

3. **Phase 3: Testing**
   - Проверить валидацию из разных директорий
   - Проверить сборку с разными выходными путями
   - Проверить индексацию

4. **Phase 4: Documentation**
   - Обновить AGENTS.md
   - Обновить README.md с примерами workspace структуры

## Open Questions

- None - все технические решения приняты
