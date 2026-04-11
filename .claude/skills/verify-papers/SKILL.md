---
title: Verify Papers
description: Verify bibliography entries (REAL/FAKE/UNCERTAIN) and generate detailed paper cards via qwen3+Perplexity
---

# Skill: verify-papers

## Моя роль (Claude = оркестратор)
- Я **не читаю** статьи сам
- Я **не формулирую** содержание карточек из памяти или по abstract
- Короткие данные (ключи, вердикт, confidence) → читаю напрямую
- Весь анализ статей → делегируется **qwen3-235b**
- Источник контента: Perplexity → arXiv → PDF → Semantic Scholar (по доступности)

**Прокси-модель:** `qwen/qwen3-235b-a22b-2507` via OpenRouter  
**Поиск:** Perplexity `sonar`

---

## Что делает скилл

Для каждой записи в `bibliography.bib`:

1. **Верифицирует** — реальна ли статья (REAL / FAKE / UNCERTAIN)
2. **Создаёт карточку** `papers_cards/<key>.md` со структурированной информацией:
   - Цель работы
   - Закрытый научный гэп
   - Метрики и датасеты
   - Конкретные результаты
   - Верификационный вердикт

Карточки используются скиллом `check-context` как источник правды о статье.

---

## Структура артефактов

```
.claude/skills/verify-papers/
├── SKILL.md               ← этот файл
├── pyproject.toml
├── tools/
│   └── verify_papers.py   ← основной скрипт
├── papers_cards/          ← карточки статей (создаётся автоматически)
│   ├── key1.md
│   ├── key2.md
│   └── ...
└── papers_results.json    ← сводный файл вердиктов (создаётся автоматически)
```

---

## Запуск

```bash
cd .claude/skills/verify-papers

# Полный прогон всех статей (кешированные пропускаются)
uv run python tools/verify_papers.py

# Тест — 5 статей, verbose
uv run python tools/verify_papers.py --test

# Перепроверить конкретные ключи (сбрасывает кеш и карточку)
uv run python tools/verify_papers.py --recheck key1 key2

# С дополнительным промптом и подсказками
uv run python tools/verify_papers.py \
  --recheck key1 key2 \
  --prompt "Pay extra attention to publication venue and year" \
  --hints key1:"check arXiv carefully" key2:"may be a book chapter"
```

---

## Workflow для Claude

### Шаг 1 — Запустить верификацию
```bash
uv run python tools/verify_papers.py --test   # сначала тест
uv run python tools/verify_papers.py          # полный прогон
```

### Шаг 2 — Прочитать сводку (короткие данные, читаю напрямую)
Прочитать `papers_results.json`, выбрать:
- `verdict == "FAKE"` → обязательный recheck
- `verdict == "UNCERTAIN"` и `confidence < 70` → recheck с уточнённым промптом

### Шаг 3 — Перепроверить подозрительные
```bash
uv run python tools/verify_papers.py \
  --recheck key1 key2 \
  --prompt "These may be preprints. Search arXiv carefully." \
  --hints key1:"look for 'Paper Title' on arXiv"
```

### Шаг 4 — Прочитать карточки (если нужен контекст)
Читать только узко: `papers_cards/<key>.md` — один файл за раз, только при необходимости.

### Шаг 5 — Сформировать итоговый отчёт для пользователя
- Сводка: REAL / FAKE / UNCERTAIN по каждой статье
- Для FAKE — рекомендация: удалить или заменить
- Для UNCERTAIN — рекомендация: проверить вручную или recheck

---

## Формат карточки

```markdown
---
key: authorYYYYkeyword
title: Full Paper Title
authors: Author1 and Author2
year: 2024
venue: Journal / Conference name
doi: 10.xxxx/xxxxx or null
arxiv_id: arXiv:2401.XXXXX or null
pdf_url: https://... or null
semantic_scholar_id: null  ← зарезервировано
verified: true/false
confidence: 0-100
source_used: perplexity | arxiv | pdf | semantic_scholar
last_checked: YYYY-MM-DD
---

## Цель работы
...

## Закрытый гэп
...

## Метрики и датасеты
...

## Результаты
...

## Верификационный вердикт
**REAL** (95%) — Paper found on arXiv:2401.XXXXX, confirmed in NeurIPS 2024 proceedings.
```

---

## Кеш и инвалидация

- Кеш: `tools/.cache/<md5(key)>.json`
- `--recheck key1` инвалидирует кеш **и** удаляет карточку для этого ключа
- Полный прогон пропускает уже закешированные записи
- Для принудительного полного перезапуска: `rm -rf tools/.cache/`

---

## Интеграция с Semantic Scholar (зарезервировано)

Поле `semantic_scholar_id` в карточке зарезервировано. Когда будет подключён `semantic_scholar.py`:
- Добавить как дополнительный источник в `verify_papers.py` (после Perplexity)
- Заполнять `semantic_scholar_id` из API-ответа
- Обновить `source_used` на `semantic_scholar` если использовался этот источник

---

## Стоимость

| Операция | Модель | ~Стоимость |
|----------|--------|------------|
| Полный прогон (~40 статей) | qwen3-235b + sonar | ~$1–3 |
| Recheck 5 статей | qwen3-235b + sonar | ~$0.15–0.50 |
| Одна статья | qwen3-235b + sonar | ~$0.03–0.08 |
