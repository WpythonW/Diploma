# check-citations tools

Инструмент для автоматической верификации библиографии диплома. Проверяет каждую записи `.bib`-файла на существование через **Perplexity Sonar** и **Semantic Scholar**, выносит вердикт REAL/FAKE/UNCERTAIN и генерирует структурированные карточки статей.

---

## Архитектура

```
tools/
├── check_papers.py          # CLI entry point — тонкая обёртка
├── parser.py                # Парсинг .bib-файлов
├── cache.py                 # Кеширование вердиктов и карточек на диск
├── card_builder.py          # Генерация markdown-карточки из вердикта
├── agent.py                 # LangChain ReAct-агент верификации
├── semantic_scholar.py      # Async-обёртка над Semantic Scholar Graph API
├── openrouter_ask.py         # Синхронный вызов LLM через OpenRouter (для контекстного анализа)
├── log_io.py                # Логирование I/O оркестратора (token usage)
├── generate_summary_table.py # Сводная таблица из papers_results.json
└── tests/
    └── test_check_papers.py  # 27 unit-тестов (без LLM-вызовов)
```

---

## Модули

### `check_papers.py` — CLI Entry Point

**Роль:** тонкий orchestrator, связывающий все модули.

**Что делает:**
1. Парсит `bibliography.bib` через `parser.parse_bib()`
2. Определяет scope (full / partial / recheck / cards-only)
3. Запускает параллельную верификацию через `run_entries()`
4. Генерирует карточки через `_generate_card()`
5. Сохраняет `papers_results.json` и запускает `generate_summary_table.py`

**CLI-флаги:**
| Флаг | Описание |
|------|----------|
| `--n N` | Проверить первые N записей |
| `--keys k1 k2` | Проверить конкретные ключи |
| `--recheck k1 k2` | Перепроверить (инвалидация кеша + карточки) |
| `--prompt "..."` | Кастомный суффикс системного промпта |
| `--hints k1:"hint" k2:"hint"` | Подсказки на ключ |
| `--no-cards` | Пропустить генерацию карточек |
| `--cards-only` | Только карточки из кеша (без верификации) |
| `--reset` | Очистить кеш, карточки, результаты |

---

### `parser.py` — Парсинг библиографии

**Роль:** извлечение структурированных данных из `.bib`-файла.

**Функции:**
| Функция | Что делает |
|---------|-----------|
| `parse_bib(filepath)` | Парсит `.bib` → `list[dict]` с полями `key`, `type`, `fields` |
| `entry_to_description(entry)` | Форматирует entry в человекочитаемое описание для агента |

Регулярки извлекают `@type{key, ...}` блоки и поля `key = {value}`. Nested `{...}` разворачиваются.

---

### `cache.py` — Кеширование на диск

**Роль:** сохранение и загрузка результатов верификации.

**Функции:**
| Функция | Что делает |
|---------|-----------|
| `cache_get(key)` | Загружает результат из `.cache/<md5(key)>.json` |
| `cache_set(key, value)` | Сохраняет результат |
| `cache_invalidate(key)` | Удаляет кеш для ключа |
| `card_path(key)` | Возвращает путь к `papers_cards/<key>.md` |
| `card_exists_and_verified(key)` | Проверяет `verified: true` в карточке |
| `card_invalidate(key)` | Удаляет карточку |

Кеш позволяет пропускать уже проверенные статьи при повторных запусках. `--recheck` инвалидирует кеш и карточку.

---

### `card_builder.py` — Генерация карточек

**Роль:** сборка markdown-карточки из верификационного результата.

**Функции:**
| Функция | Что делает |
|---------|-----------|
| `build_card(entry, result, card_body)` | Собирает итоговый `.md` файл карточки |

`card_body` приходит от LLM (qwen3), `build_card` оборачивает его в структурированный шаблон с frontmatter (key, title, authors, year, venue, DOI, arXiv, verified, confidence), секциями (Goal, Gap Addressed, Method, Datasets and Metrics, Results, Limitations, Verification Verdict) и ссылками (Semantic Scholar, DOI, arXiv, PDF).

---

### `agent.py` — LangChain ReAct-агент

**Роль:** ядро верификации — async ReAct-агент с двумя инструментами поиска.

**Как работает:**
1. **Prefetch S2** — параллельно с другими агентами делает запрос к Semantic Scholar
2. **Определяет LangChain-инструменты** — `search_perplexity_tool` и `search_s2_tool` через `@tool` decorator
3. **Создаёт ReAct graph** — `create_react_agent(llm, tools)` из LangGraph
4. **Запускает агент** — LLM сам решает, какой инструмент вызвать, LangGraph dispatch-ит параллельно
5. **Парсит вердикт** — извлекает JSON-блок `{"verdict": "REAL|FAKE|UNCERTAIN", "confidence": 0-100, "reason": "..."}`

Использует `ChatOpenAI` (langchain-openai) с моделью `qwen/qwen3-235b-a22b-2507` через OpenRouter.

---

### `semantic_scholar.py` — Semantic Scholar API

**Роль:** async-обёртка над Semantic Scholar Graph API.

**Стратегия поиска:**
1. Поиск по title → выбирает лучший hit по token-overlap similarity + совпадение года
2. Если sim < 0.6 — повторный поиск с фамилией первого автора
3. Возвращает `SemanticScholarResult` (DOI, arXiv, PDF URL, citation count, venue)

Без API-кей: 1 req/s. С `S2_API_KEY` в `.env`: 10 req/s.

---

### `openrouter_ask.py` — Синхронный LLM-вызов

**Роль:** standalone вызов LLM для контекстного анализа (Step 4 в workflow).

Используется когда нужно проверить, как именно цитируется FAKE/UNCERTAIN статья в тексте диплома. Берёт параграф `.tex`-файла + информацию о статье → отправляет qwen3 → получает вердикт OK/SUSPICIOUS/WRONG.

---

### `log_io.py` — Логирование I/O

**Роль:** трассировка запросов к LLM для прозрачности token usage.

**Функции:**
| Функция | Что делает |
|---------|-----------|
| `log_out(label, text)` | Логирует отправленный промпт |
| `log_in(label, text)` | Логирует полученный ответ |
| `print_token_summary()` | Выводит суммарный IN/OUT в чарах и токенах (~chars/4) |

Формат: JSONL в `orchestrator_io.log`.

---

### `generate_summary_table.py` — Сводная таблица

**Роль:** генерация `papers_summary_table.md` из `papers_results.json`.

Сортирует: FAKE → UNCERTAIN → REAL. Для каждой записи: key, verdict, confidence, searches, goal (из карточки), reason.

---

## Workflow

```
.bib  →  parser.parse_bib()  →  list[entry]
                                      │
                                      ▼
                          ┌──── run_entries() ────┐
                          │   (async, N parallel)  │
                          │                        │
                          │  agent.py (ReAct)      │
                          │  ├─ search_perplexity  │
                          │  └─ search_s2_tool     │
                          │         │              │
                          │         ▼              │
                          │  verdict + confidence  │
                          │         │              │
                          │         ▼              │
                          │  card_builder.build    │
                          └────────────────────────┘
                                      │
                                      ▼
                    papers_results.json  +  papers_cards/*.md
                                      │
                                      ▼
                          generate_summary_table.py
                                      │
                                      ▼
                          papers_summary_table.md
```

### Этапы верификации одной статьи

1. **Prefetch** — асинхронный запрос к Semantic Scholar (параллельно с другими агентами)
2. **ReAct loop** — LangGraph агент вызывает Perplexity и/или S2 (до 8 итераций)
3. **Cross-check** — сопоставление title, authors, year, venue из обоих источников
4. **Verdict** — REAL / FAKE / UNCERTAIN + confidence 0-100 + reason
5. **Card generation** — LLM генерирует структурированную карточку из search results
6. **Cache** — результат сохраняется, следующий запуск пропускает verified entries

### Recheck pipeline

Для оспоренных записей:
1. Инвалидация кеша и карточки
2. Перезапуск с кастомным `--prompt` и per-key `--hints`
3. Параллельный прогон всех disputed entries

### Context analysis (Step 4 из SKILL.md)

Для FAKE/UNCERTAIN записей:
1. `grep` по `.tex`-файлам — найти где цитируется
2. Прочитать ±10 строк вокруг цитаты
3. Отправить параграф + статью в qwen3 через `openrouter_ask.py`
4. Вердикт: OK / SUSPICIOUS / WRONG → арбитраж

---

## Зависимости

API-кей в `.env` (repo root или parent):
- `OPENROUTER_API_KEY` — для qwen3 через OpenRouter
- `PERPLEXITY_API_KEY` — для sonar поиска
- `S2_API_KEY` (опционально) — для Semantic Scholar (10 req/s вместо 1)
