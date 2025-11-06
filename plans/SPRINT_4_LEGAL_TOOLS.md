# Sprint 4: Legal & Practical Tools

**Status:** 🚧 Code written, not merged to main
**Priority:** Medium (not critical for core bot)
**Branch:** claude/review-safety-protocols-011CUqbQc2eb7S731CdMttL9
**Estimated completion:** 15-20% additional to project

---

## 🎯 Цели спринта

Создать практические инструменты для родителей, переживающих Parental Alienation, для:
1. Документирования взаимодействий (legal admissibility)
2. Конструктивной коммуникации (BIFF, NVC)
3. Подготовки к медиации
4. Выбора модели со-родительства

---

## 📋 Задачи

### 1. Contact Diary System
**Цель:** Юридически допустимый дневник контактов

**Требования:**
- Фиксация даты/времени каждого взаимодействия
- Запись фактов (не эмоций)
- Export в PDF для суда
- Шифрование данных (GDPR compliance)

**Функции:**
- `/diary_entry` - добавить запись
- `/diary_view` - просмотр истории
- `/diary_export` - экспорт в PDF

**Файлы:**
- `src/tools/contact_diary.py`
- `src/tools/pdf_exporter.py`

**Критерии готовности:**
- [ ] Можно добавлять записи через бота
- [ ] Данные шифруются
- [ ] Export в PDF работает
- [ ] Формат соответствует legal requirements

---

### 2. BIFF Template System
**Цель:** Помощь в написании Brief, Informative, Friendly, Firm сообщений

**Требования:**
- Шаблоны для типичных ситуаций
- Проверка сообщения на BIFF compliance
- Предложения по улучшению

**Функции:**
- `/biff_template` - выбрать шаблон
- `/biff_check` - проверить сообщение
- Интеграция с NVC transformer

**Файлы:**
- `src/letters/biff_templates.py`
- `config/biff_templates.json`

**Критерии готовности:**
- [ ] 5-10 базовых шаблонов
- [ ] Проверка текста на BIFF
- [ ] Интеграция с NVC

---

### 3. Mediation Preparation
**Цель:** Помощь в подготовке к медиации

**Требования:**
- Checklist для подготовки
- Стратегии для разных сценариев
- Документы для сбора

**Функции:**
- `/mediation_prep` - начать подготовку
- Guided questionnaire
- Personalized recommendations

**Файлы:**
- `src/tools/mediation_prep.py`
- `config/mediation_scenarios.json`

**Критерии готовности:**
- [ ] Checklist готов
- [ ] 3-5 основных сценариев
- [ ] Recommendations работают

---

### 4. Co-Parenting vs Parallel Parenting Decision Tree
**Цель:** Помочь выбрать подходящую модель

**Требования:**
- Assessment текущей ситуации
- Decision tree на основе факторов
- Рекомендации по реализации

**Функции:**
- `/parenting_model` - пройти assessment
- Сравнение моделей
- Action plan для выбранной модели

**Файлы:**
- `src/tools/parenting_model_advisor.py`
- `config/parenting_models.json`

**Критерии готовности:**
- [ ] Assessment questionnaire готов
- [ ] Decision logic реализована
- [ ] Рекомендации работают

---

## 🔗 Зависимости

### От предыдущих спринтов:
- ✅ Sprint 1: Safety protocols (для проверки контента)
- ✅ Sprint 2: NVC transformer (для BIFF integration)
- ✅ Sprint 3: Quality control (для проверки рекомендаций)

### Внешние зависимости:
- PDF library (ReportLab или WeasyPrint)
- Legal document templates
- Clinical review для mediation advice

---

## 📊 Метрики успеха

| Метрика | Target |
|---------|--------|
| Diary entries created | > 0 (работает) |
| BIFF templates used | > 0 (работает) |
| PDF exports successful | 100% |
| Mediation prep completions | > 0 |
| Parenting model assessments | > 0 |

---

## ⚠️ Риски и вопросы

### Риски:
1. **Legal compliance:** Нужна проверка юриста для diary format
2. **PDF generation:** Может быть сложно на разных платформах
3. **Clinical advice:** Mediation recommendations нужно проверить с терапевтом

### Вопросы:
1. Нужен ли Sprint 4 до production?
   - **Мнение:** Не критично, можно сделать после MVP
2. Как хранить diary entries?
   - **Решение:** Encrypted в PostgreSQL
3. Формат PDF для суда?
   - **TODO:** Проконсультироваться с юристом

---

## 🚀 Next Steps

### Option A: Merge сейчас
1. Review code в ветке
2. Тестирование
3. Merge to main
4. **Result:** Project completeness 85%

### Option B: Отложить
1. Сфокусироваться на Sprint 5 (Metrics)
2. Довести core bot до production
3. Sprint 4 делать после MVP
4. **Result:** Faster to production

### Option C: Доработать
1. Добавить тесты
2. Clinical review
3. Legal review
4. Потом merge

---

## 📁 Код

**Ветка:** claude/review-safety-protocols-011CUqbQc2eb7S731CdMttL9
**Коммит:** 9609619 "Implement Sprint 4: Legal Tools"

**Проверить код:**
```bash
git checkout claude/review-safety-protocols-011CUqbQc2eb7S731CdMttL9
git diff main --stat
```

---

## 💡 Рекомендация

**Мое мнение:** Отложить Sprint 4 до после production MVP

**Причины:**
1. Не критично для core functionality
2. Sprint 5 (metrics) важнее для production readiness
3. Требует legal/clinical review
4. Core therapeutic bot уже работает

**Альтернатива:**
- Merge basic BIFF templates (easy)
- Остальное делать post-MVP
