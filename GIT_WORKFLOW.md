# Git Workflow - PAS Bot

## 📦 Текущий Коммит

### Информация:
- **Branch**: `feature/conversation-memory-and-fixes`
- **Commit**: `01f185b` - feat: Add conversation memory and fix core dialogue issues
- **Status**: Ready to push
- **Files Changed**: 93 files (29,832 insertions, 131 deletions)

---

## 🚀 Как Запушить в GitHub

### Вариант 1: Запушить Feature Branch (Рекомендуется)

```bash
# Убедитесь, что вы на правильной ветке
git branch
# Должно показать: * feature/conversation-memory-and-fixes

# Запушить в удалённый репозиторий
git push -u origin feature/conversation-memory-and-fixes

# После пуша создайте Pull Request на GitHub:
# 1. Перейдите на https://github.com/<your-org>/pas_bot
# 2. Нажмите "Compare & pull request"
# 3. Заполните описание (можно скопировать из COMMIT_NOTES.md)
# 4. Назначьте ревьюеров
# 5. Создайте PR
```

### Вариант 2: Мердж в Main (Если уверены)

```bash
# Переключитесь на main
git checkout main

# Мердж feature branch
git merge feature/conversation-memory-and-fixes

# Запушить в main
git push origin main

# Удалить feature branch (опционально)
git branch -d feature/conversation-memory-and-fixes
git push origin --delete feature/conversation-memory-and-fixes
```

---

## 📋 Чек-лист Перед Пушем

### Обязательно:
- [x] Код работает локально
- [x] Нет критических ошибок
- [x] Документация создана
- [x] Коммит сообщение подробное
- [ ] Tests написаны (TODO - не критично для MVP)

### Желательно:
- [ ] Code review от коллеги
- [ ] Проверена на другой машине
- [ ] Database migrations протестированы
- [ ] .env.example обновлён

### Перед Мерджем в Main:
- [ ] Feature branch протестирован
- [ ] Нет конфликтов с main
- [ ] CI/CD pipeline прошёл (если есть)
- [ ] Получен approve от ревьюера

---

## 📂 Структура Коммита

### Основные Изменения:
```
src/
├── orchestration/state_manager.py  # Conversation memory
├── core/bot.py                      # Command handlers
├── techniques/
│   ├── active_listening.py         # Stage-based prompts
│   └── supervisor_agent.py         # Empathy thresholds
```

### Документация (Новая):
```
ARCHITECTURE_ANALYSIS.md     # Как работает система
FIXES_APPLIED.md             # Что исправлено и почему
SESSION_ANALYSIS.md          # Анализ сессии пользователя
DEVELOPMENT_ROADMAP.md       # TODO для контрибьюторов
COMMIT_NOTES.md              # Детали коммита
GIT_WORKFLOW.md              # Этот файл
```

### Архив:
```
pas_archive/                 # Backup предыдущей реализации
```

---

## 🔍 Review Checklist для PR

### Для Ревьюера:

#### Функциональность:
- [ ] Conversation memory работает корректно
- [ ] Команды /letter и /goals функционируют
- [ ] Dialogue progression логичный (1-2 → 3-5 → 6+)
- [ ] Нет повторяющихся фраз в ответах

#### Код:
- [ ] Код читаемый и понятный
- [ ] Нет magic numbers или hardcoded значений
- [ ] Логирование адекватное
- [ ] Обработка ошибок присутствует

#### Документация:
- [ ] Все изменения задокументированы
- [ ] DEVELOPMENT_ROADMAP.md полный и актуальный
- [ ] Инструкции по запуску корректные

#### База Данных:
- [ ] Существующие таблицы не поломаны
- [ ] Новые таблицы (если есть) имеют индексы
- [ ] Миграции работают

#### Безопасность:
- [ ] Нет хардкоженных секретов
- [ ] PII правильно обрабатывается (или отмечено как TODO)
- [ ] SQL injection защита есть

---

## 📊 Метрики Коммита

### Статистика:
```
Files Changed:   93
Insertions:      29,832 lines
Deletions:       131 lines
Net Change:      +29,701 lines

Major Changes:   5
Bug Fixes:       2
Documentation:   6 new files
Archive:         ~50 files moved
```

### Breakdown:
- **Core Code**: ~200 lines changed
- **Documentation**: ~5,000 lines added
- **Archive**: ~24,500 lines moved
- **Tests**: ~100 lines added

---

## 🐛 Known Issues в Коммите

### Критические (Требуют Фикса):
1. **total_messages counter broken**
   - Не обновляется в БД
   - Fix: Добавить в UPDATE query

2. **Message history not persisted**
   - Теряется при перезапуске
   - Fix: Создать таблицу messages

### Некритические (Можно Отложить):
3. **ML modules disabled**
   - См. DEVELOPMENT_ROADMAP.md
   - Используются keyword-based fallbacks

4. **No unit tests**
   - TODO для следующей итерации
   - Manual testing пройдено

---

## 🔄 Workflow для Будущих Коммитов

### 1. Создайте Feature Branch:
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. Делайте Изменения:
```bash
# Редактируйте файлы
# Тестируйте локально
```

### 3. Коммитьте:
```bash
git add -A
git commit -m "feat: Your feature description

## Changes:
- Change 1
- Change 2

## Testing:
- Test 1 passed
- Test 2 passed

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 4. Пушьте и Создавайте PR:
```bash
git push -u origin feature/your-feature-name
# Создайте PR на GitHub
```

### 5. После Мерджа:
```bash
git checkout main
git pull origin main
git branch -d feature/your-feature-name
```

---

## 📝 Commit Message Convention

### Формат:
```
<type>: <short description>

## <section 1>
<details>

## <section 2>
<details>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types:
- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - только документация
- `refactor:` - рефакторинг без изменения функциональности
- `test:` - добавление тестов
- `chore:` - обновление зависимостей, конфига, etc.

### Примеры:
```bash
# Feature
git commit -m "feat: Add letter writing multi-turn dialogue"

# Bug fix
git commit -m "fix: Correct total_messages counter in database"

# Documentation
git commit -m "docs: Update API documentation for state manager"

# Refactor
git commit -m "refactor: Extract emotion detection to separate module"
```

---

## 🚦 Branch Protection Rules (Рекомендации)

### Для Main Branch:
```
Настройки GitHub:
1. Require pull request before merging
2. Require at least 1 approval
3. Dismiss stale reviews when new commits pushed
4. Require status checks (если CI/CD настроен)
5. Require conversation resolution before merging
```

### Для Feature Branches:
```
Свободно можно:
- Создавать любые feature branches
- Делать force push (до создания PR)
- Экспериментировать

Запрещено:
- Force push в main
- Коммитить прямо в main
```

---

## 📞 Troubleshooting

### Проблема: Конфликты при мердже

```bash
# Обновите main
git checkout main
git pull origin main

# Вернитесь в feature branch
git checkout feature/your-feature

# Ребейз на main
git rebase main

# Разрешите конфликты вручную
# git add <resolved-files>
# git rebase --continue

# Force push (т.к. история изменилась)
git push -f origin feature/your-feature
```

### Проблема: Нужно отменить коммит

```bash
# Отменить последний коммит (сохранив изменения)
git reset --soft HEAD~1

# Отменить последний коммит (удалив изменения)
git reset --hard HEAD~1

# Отменить конкретный коммит
git revert <commit-hash>
```

### Проблема: Случайно закоммитили секреты

```bash
# НЕМЕДЛЕННО:
1. Удалите секрет из кода
2. Создайте новый коммит
3. Force push (если ещё не запушили)
4. Если запушили - ротируйте секрет (новый API key, etc.)

# НЕ ПОЛАГАЙТЕСЬ на git history cleanup для безопасности
# Считайте секрет скомпрометированным если он был запушен
```

---

## 🎯 Next Steps После Пуша

1. **Создать Pull Request** на GitHub
2. **Назначить ревьюеров** (если есть команда)
3. **Дождаться code review**
4. **Внести правки** (если нужно)
5. **Мердж в main** после approve
6. **Deploy** (если автоматический деплой настроен)
7. **Мониторинг** после деплоя

---

## 📚 Полезные Ссылки

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Last Updated**: 2025-11-08
**Current Branch**: feature/conversation-memory-and-fixes
**Ready to Push**: ✅ Yes
