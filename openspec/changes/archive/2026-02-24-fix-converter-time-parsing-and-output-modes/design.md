## Context

Текущая реализация `convert_script.py` содержит функцию `parse_time()` которая не поддерживает формат `MM:SS:mmm` (минуты:секунды:миллисекунды), используемый в таблице скриптов. Это приводит к некорректному вычислению поля `trim` в JSON.

Также обе утилиты (`convert_script.py` и `check.py`) не имеют гибкого управления выводом, что затрудняет их использование в разных сценариях: интерактивном, отладочном и автоматическом.

## Goals / Non-Goals

**Goals:**
1. Исправить парсинг времени для поддержки формата `MM:SS:mmm`
2. Добавить три режима вывода: normal, verbose (`-v`), quiet (`-q`)
3. Обеспечить обратную совместимость (default behavior = normal mode)
4. Обновить документацию в AGENTS.md

**Non-Goals:**
- Изменение структуры JSON выходного файла
- Изменение формата таблицы в MD
- Добавление новых зависимостей
- Изменение API Shotstack

## Decisions

### Decision 1: Time Parsing Implementation
**Choice:** Расширить `parse_time()` для поддержки 3-компонентного формата

**Rationale:**
- Минимальные изменения существующего кода
- Обратная совместимость с существующими форматами `MM:SS` и `HH:MM:SS`
- Простота реализации

**Implementation:**
```python
def parse_time(time_str: str) -> float:
    parts = time_str.strip().split(":")
    if len(parts) == 3:  # MM:SS:mmm
        minutes, seconds, ms = map(int, parts)
        return minutes * 60 + seconds + ms / 1000
    # ... existing code
```

### Decision 2: Output Mode Architecture
**Choice:** Использовать глобальный logger/verbosity level вместо передачи флагов через все функции

**Rationale:**
- Позволяет избежать изменения сигнатур множества функций
- Стандартный паттерн в Python CLI tools
- Простота поддержки

**Alternatives considered:**
- Передача `verbose` параметра через всю цепочку вызовов - отклонено из-за большого количества изменений
- Использование logging module - избыточно для данной задачи

**Implementation:**
```python
# Глобальная переменная уровня детализации
VERBOSITY = 0  # 0=normal, 1=verbose, -1=quiet

def log_verbose(message: str):
    if VERBOSITY >= 1:
        print(message)

def log_normal(message: str):
    if VERBOSITY >= 0:
        print(message)
```

### Decision 3: Argument Parsing Strategy
**Choice:** Использовать простой ручной парсинг аргументов (как сейчас) вместо argparse

**Rationale:**
- Минимальные изменения кода
- Сохранение текущего стиля проекта
- Достаточно для простых флагов `-v` и `-q`

**Implementation:**
```python
args = sys.argv[1:]
verbose = "-v" in args or "--verbose" in args
quiet = "-q" in args or "--quiet" in args
# Remove flags from args before processing
args = [a for a in args if a not in ("-v", "--verbose", "-q", "--quiet")]
```

## Risks / Trade-offs

**[Risk]** Неправильное определение формата времени → **Mitigation:** Добавить тесты для различных форматов

**[Risk]** Конфликт флагов `-v` и `-q` → **Mitigation:** Приоритет quiet > verbose, или выдавать ошибку если оба указаны

**[Risk]** Breaking change для пользователей, ожидающих текущий verbose вывод → **Mitigation:** Сохранить normal mode как default с минимальным выводом

## Migration Plan

1. **Update convert_script.py:**
   - Добавить глобальную переменную `VERBOSITY`
   - Исправить `parse_time()` для MM:SS:mmm
   - Добавить функции `log_verbose()`, `log_normal()`, `log_quiet()`
   - Обновить `main()` для парсинга флагов
   - Заменить существующие `print()` на соответствующие log функции

2. **Update check.py:**
   - Добавить поддержку `-q` флага
   - Обновить `print_report()` для учета quiet mode

3. **Update AGENTS.md:**
   - Добавить описание новых флагов в разделе команд

## Open Questions

- None - все технические решения приняты
