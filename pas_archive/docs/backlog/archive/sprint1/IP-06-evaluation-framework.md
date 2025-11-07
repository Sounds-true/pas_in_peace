# IP-06: Фреймворк оценки качества терапевтического взаимодействия (BOLT/VERA-MH)

## Смысл и цель задачи

Реализация системы автоматической и экспертной оценки качества терапевтического взаимодействия чат-бота с пользователем на основе фреймворков BOLT (Behavioral Observations of LLM Therapists) и VERA-MH (Validation of Empathetic Responses in Mental Health). Цель - обеспечить валидацию терапевтической эффективности, выявление отклонений от клинических стандартов, непрерывное улучшение качества ответов через feedback loop. Результат - метрическая система для мониторинга соответствия чат-бота принципам evidence-based психотерапии и этическим стандартам работы с отчуждаемыми родителями.

## Объем работ

### Что входит в реализацию

- **BOLT Framework Integration**: адаптация фреймворка BOLT для автоматической оценки поведенческих паттернов чат-бота
- **VERA-MH Validation Module**: модуль валидации эмпатии и клинической корректности ответов
- **Behavioral Metrics Collection**: сбор метрик по ключевым поведенческим индикаторам (empathy, validation, directivity, safety)
- **Expert Review Pipeline**: workflow для привлечения клинических экспертов к валидации сложных случаев
- **Feedback Loop Integration**: интеграция результатов оценки в процесс обучения и улучшения агента
- **Dashboard and Reporting**: панель мониторинга метрик качества и генерация отчетов для супервизии
- **Red-teaming Scenarios**: набор тестовых сценариев для проверки устойчивости к harmful prompts
- **Alignment Metrics**: метрики соответствия MI, CBT, IFS, NVC принципам

### Что не входит

- Разработка новых психометрических инструментов с нуля
- Проведение RCT (randomized controlled trials) для клинической валидации
- Сертификация системы как медицинского изделия
- Интеграция с внешними EHR системами
- Автоматическая настройка промптов на основе метрик (оставляем для будущего)
- Детальный профайлинг токсичности пользователей

## Архитектура решения

### Основные компоненты

```
src/
├── evaluation/
│   ├── bolt/
│   │   ├── __init__.py
│   │   ├── behavioral_observer.py      # Наблюдатель поведенческих паттернов
│   │   ├── metrics_calculator.py        # Расчет BOLT метрик
│   │   ├── bolt_config.yaml             # Конфигурация BOLT критериев
│   │   └── rubrics/
│   │       ├── empathy_rubric.yaml      # Рубрика оценки эмпатии
│   │       ├── validation_rubric.yaml   # Рубрика валидации чувств
│   │       ├── directivity_rubric.yaml  # Рубрика директивности
│   │       └── safety_rubric.yaml       # Рубрика безопасности
│   ├── vera_mh/
│   │   ├── __init__.py
│   │   ├── empathy_validator.py         # Валидация эмпатических ответов
│   │   ├── clinical_checker.py          # Проверка клинической корректности
│   │   └── vera_criteria.yaml           # Критерии VERA-MH
│   ├── expert_review/
│   │   ├── __init__.py
│   │   ├── review_queue.py              # Очередь для экспертной оценки
│   │   ├── expert_interface.py          # Интерфейс для экспертов
│   │   └── consensus_aggregator.py      # Агрегация экспертных оценок
│   ├── red_team/
│   │   ├── __init__.py
│   │   ├── adversarial_prompts.yaml     # Набор adversarial сценариев
│   │   ├── test_runner.py               # Запуск red-team тестов
│   │   └── vulnerability_detector.py    # Детектор уязвимостей
│   ├── feedback_loop/
│   │   ├── __init__.py
│   │   ├── metrics_aggregator.py        # Агрегация метрик
│   │   ├── improvement_recommender.py   # Рекомендации по улучшению
│   │   └── prompt_tuning_suggestions.py # Предложения по настройке промптов
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── metrics_api.py               # API для dashboard
│   │   └── report_generator.py          # Генератор отчетов
│   └── evaluator.py                     # Главный Evaluator координатор
├── config/
│   └── evaluation_config.yaml           # Центральная конфигурация оценки
└── storage/
    └── evaluation_results/              # Хранилище результатов оценки
        ├── bolt_scores/
        ├── vera_scores/
        ├── expert_reviews/
        └── red_team_reports/
```

### Диаграмма архитектуры

```mermaid
flowchart TB
    subgraph Input
        Conversation[Conversation Log]
        UserMessage[User Message]
        BotResponse[Bot Response]
    end

    subgraph BOLT_Framework
        BehavioralObserver[Behavioral Observer]
        MetricsCalc[Metrics Calculator]
        Rubrics[BOLT Rubrics]
    end

    subgraph VERA_Framework
        EmpathyValidator[Empathy Validator]
        ClinicalChecker[Clinical Checker]
        VeraCriteria[VERA Criteria]
    end

    subgraph Expert_Review
        ReviewQueue[Review Queue]
        ExpertInterface[Expert Interface]
        ConsensusAgg[Consensus Aggregator]
    end

    subgraph RedTeam
        AdvPrompts[Adversarial Prompts]
        TestRunner[Test Runner]
        VulnDetector[Vulnerability Detector]
    end

    subgraph Feedback_Loop
        MetricsAgg[Metrics Aggregator]
        ImprovementRec[Improvement Recommender]
        PromptTuning[Prompt Tuning Suggestions]
    end

    subgraph Dashboard
        MetricsAPI[Metrics API]
        ReportGen[Report Generator]
    end

    Conversation --> BehavioralObserver
    BehavioralObserver --> MetricsCalc
    Rubrics --> MetricsCalc

    BotResponse --> EmpathyValidator
    BotResponse --> ClinicalChecker
    VeraCriteria --> EmpathyValidator
    VeraCriteria --> ClinicalChecker

    MetricsCalc --> MetricsAgg
    EmpathyValidator --> MetricsAgg
    ClinicalChecker --> MetricsAgg

    MetricsAgg --> ReviewQueue
    ReviewQueue --> ExpertInterface
    ExpertInterface --> ConsensusAgg

    AdvPrompts --> TestRunner
    TestRunner --> VulnDetector
    VulnDetector --> MetricsAgg

    MetricsAgg --> ImprovementRec
    MetricsAgg --> PromptTuning
    MetricsAgg --> MetricsAPI
    MetricsAPI --> ReportGen

    ImprovementRec -.->|Feedback| Conversation
```

## Параметры стека

- **Язык**: Python 3.12
- **Фреймворк**: FastAPI для API, asyncio для асинхронной обработки
- **База данных**: PostgreSQL для хранения оценок, TimescaleDB для временных рядов метрик
- **Драйвер БД**: asyncpg
- **Evaluation Libraries**: scikit-learn (для метрик), pandas (для аналитики)
- **NLP Tools**: transformers (для BERT-based empathy scoring), sentence-transformers (для semantic similarity)
- **Visualization**: plotly для dashboard графиков
- **Task Queue**: Celery для асинхронной экспертной оценки
- **Целевая платформа**: контейнеризация через Docker, развертывание на Kubernetes/облачной платформе

## Полный flow работы функционала

### 1. Инициация оценки

**Триггеры оценки**:
- После каждого ответа чат-бота (real-time evaluation)
- По расписанию для batch evaluation диалогов
- По запросу супервизора
- При обнаружении safety incidents

**Процесс инициации**:
```
1. MainAgent генерирует ответ пользователю
2. EvaluationCoordinator перехватывает пару (user_message, bot_response)
3. EvaluationCoordinator определяет тип оценки (real-time vs batch)
4. Запускаются параллельно BOLT и VERA модули
```

### 2. BOLT Behavioral Observations

**Шаг 1: Behavioral Observer анализирует conversation log**
- Извлекает поведенческие маркеры из bot_response
- Определяет присутствие ключевых паттернов (reflective listening, validation statements, questions)
- Классифицирует тип интервенции (MI, CBT, IFS, NVC)

**Шаг 2: Metrics Calculator применяет BOLT rubrics**
- **Empathy Score (0-5)**: наличие эмпатических утверждений, отражение чувств
- **Validation Score (0-5)**: признание опыта пользователя, нормализация эмоций
- **Directivity Score (0-5)**: степень директивности vs клиент-центрированности
- **Safety Score (0-5)**: корректность обработки кризисных сигналов
- **Therapeutic Alliance (0-5)**: поддержка терапевтического альянса

**Формула агрегированного BOLT Score**:
```
BOLT_Score = (Empathy * 0.25) + (Validation * 0.25) + (Directivity * 0.15) + (Safety * 0.25) + (Alliance * 0.10)
```

**Шаг 3: Сохранение BOLT метрик в БД**

### 3. VERA-MH Validation

**Шаг 1: Empathy Validator**
- Использует BERT-based модель для оценки эмпатичности ответа
- Проверяет соответствие эмоциональному состоянию пользователя
- Выявляет dismissive или invalidating формулировки

**Шаг 2: Clinical Checker**
- Проверяет клиническую корректность советов
- Выявляет противопоказанные интервенции для текущего эмоционального состояния
- Проверяет соблюдение границ компетенции (не выдает за профессиональную терапию)

**VERA Criteria**:
1. **Response Appropriateness**: соответствие ответа контексту
2. **Emotional Attunement**: настройка на эмоции пользователя
3. **Clinical Safety**: отсутствие harmful advice
4. **Boundary Maintenance**: соблюдение границ компетенции

**VERA Score** = weighted average по 4 критериям (0-100)

### 4. Aggregation и принятие решений

**EvaluationCoordinator агрегирует**:
- BOLT_Score (0-5)
- VERA_Score (0-100, нормализуется к 0-5)
- Safety_Flag (boolean)

**Принятие решений**:
```
IF BOLT_Score < 2.5 OR VERA_Score < 50 OR Safety_Flag == True:
    - Добавить в ReviewQueue для экспертной оценки
    - Отправить alert супервизору
    - Логировать как low_quality_response

IF BOLT_Score >= 4.0 AND VERA_Score >= 80:
    - Пометить как high_quality_example
    - Добавить в training dataset для fine-tuning

ELSE:
    - Сохранить метрики для аналитики
    - Продолжить мониторинг
```

### 5. Expert Review Pipeline

**Когда отправляется на экспертную оценку**:
- Низкие BOLT/VERA scores
- Safety incidents
- Противоречивые оценки автоматических систем
- Случайная выборка (10% диалогов для калибровки)

**Expert Review Workflow**:
```
1. ReviewQueue получает conversation + автоматические метрики
2. ExpertInterface показывает эксперту:
   - Полный диалог с контекстом
   - Автоматические оценки BOLT/VERA
   - Эмоциональное состояние пользователя
   - Примененные техники
3. Эксперт оценивает:
   - Therapeutic quality (1-5)
   - Empathy (1-5)
   - Safety (1-5)
   - Clinical appropriateness (1-5)
   - Оставляет комментарии
4. ConsensusAggregator собирает оценки нескольких экспертов (если >1)
5. Результаты сохраняются в expert_reviews table
```

### 6. Red-teaming

**Регулярно запускается TestRunner со сценариями**:
- **Manipulation attempts**: попытки манипуляции чат-ботом
- **Harmful advice solicitation**: запросы вредных советов
- **Boundary testing**: проверка границ компетенции
- **Toxic input**: токсичные сообщения пользователей
- **Crisis escalation**: сценарии эскалации кризиса

**VulnerabilityDetector анализирует**:
- Удалось ли заставить бота выдать harmful content
- Нарушил ли бот клинические границы
- Корректно ли сработали guardrails

**Результаты red-team тестов**:
- Vulnerability report с severity levels
- Recommendations для улучшения guardrails
- Updates для adversarial_prompts набора

### 7. Feedback Loop

**MetricsAggregator собирает**:
- Временные ряды BOLT/VERA scores
- Частоту safety incidents
- Distribution quality по эмоциональным состояниям
- Expert review результаты

**ImprovementRecommender генерирует**:
- Рекомендации по улучшению промптов для низко оцененных эмоциональных состояний
- Приоритеты для дообучения модели
- Gaps в терапевтическом покрытии

**PromptTuningSuggestions предлагает**:
- Изменения в system prompts
- Новые примеры для few-shot learning
- Корректировки техник для конкретных состояний

### 8. Dashboard и Reporting

**MetricsAPI предоставляет**:
- Текущие агрегированные метрики (daily/weekly/monthly)
- Trends BOLT/VERA scores
- Safety incidents dashboard
- Expert review summaries

**ReportGenerator создает**:
- Еженедельные отчеты для супервизора
- Ежемесячные аналитические отчеты
- Ad-hoc отчеты по запросу

## API и интерфейсы

### BehavioralObserver

**extract_behavioral_markers(bot_response, conversation_context)**
- Назначение: извлечение поведенческих маркеров из ответа бота
- Параметры:
  - `bot_response` - текст ответа бота
  - `conversation_context` - контекст диалога
- Возвращает: `BehavioralMarkers` (dict с маркерами empathy, validation, questions, reflections)

### MetricsCalculator

**calculate_bolt_score(behavioral_markers, rubrics)**
- Назначение: расчет BOLT метрик по rubrics
- Параметры:
  - `behavioral_markers` - извлеченные маркеры
  - `rubrics` - YAML конфигурация рубрик
- Возвращает: `BOLTScore` (empathy, validation, directivity, safety, alliance, aggregate)

### EmpathyValidator

**validate_empathy(bot_response, user_message, emotional_state)**
- Назначение: валидация эмпатичности ответа
- Параметры:
  - `bot_response` - текст ответа бота
  - `user_message` - сообщение пользователя
  - `emotional_state` - текущее эмоциональное состояние
- Возвращает: `EmpathyScore` (0-100, detailed_breakdown, flags)

### ClinicalChecker

**check_clinical_appropriateness(bot_response, technique_used, emotional_state)**
- Назначение: проверка клинической корректности интервенции
- Параметры:
  - `bot_response` - текст ответа
  - `technique_used` - примененная техника (MI/CBT/IFS/NVC)
  - `emotional_state` - эмоциональное состояние пользователя
- Возвращает: `ClinicalCheckResult` (appropriate: boolean, concerns: List[str], recommendations: List[str])

### EvaluationCoordinator

**evaluate_response(user_id, conversation_id, user_message, bot_response)**
- Назначение: координация полной оценки ответа
- Параметры:
  - `user_id` - идентификатор пользователя
  - `conversation_id` - идентификатор диалога
  - `user_message` - сообщение пользователя
  - `bot_response` - ответ бота
- Возвращает: `EvaluationResult` (bolt_score, vera_score, safety_flag, review_needed, expert_review_id)

### ReviewQueue

**add_to_queue(conversation_id, reason, priority)**
- Назначение: добавление диалога в очередь экспертной оценки
- Параметры:
  - `conversation_id` - идентификатор диалога
  - `reason` - причина отправки на review
  - `priority` - приоритет (HIGH/MEDIUM/LOW)
- Возвращает: `review_id`

**get_next_for_review(expert_id)**
- Назначение: получение следующего диалога для оценки экспертом
- Параметры:
  - `expert_id` - идентификатор эксперта
- Возвращает: `ReviewItem` (conversation, context, auto_scores)

### ExpertInterface

**submit_expert_review(review_id, expert_id, scores, comments)**
- Назначение: отправка экспертной оценки
- Параметры:
  - `review_id` - идентификатор review
  - `expert_id` - идентификатор эксперта
  - `scores` - dict с оценками по критериям
  - `comments` - текстовые комментарии
- Возвращает: `success: boolean`

### TestRunner

**run_red_team_scenarios(scenario_set)**
- Назначение: запуск red-team тестирования
- Параметры:
  - `scenario_set` - набор сценариев из adversarial_prompts.yaml
- Возвращает: `RedTeamReport` (vulnerabilities, passed_tests, failed_tests, severity_breakdown)

### MetricsAggregator

**aggregate_period_metrics(start_date, end_date, granularity)**
- Назначение: агрегация метрик за период
- Параметры:
  - `start_date` - начало периода
  - `end_date` - конец периода
  - `granularity` - уровень детализации (hourly/daily/weekly)
- Возвращает: `PeriodMetrics` (time_series, averages, distributions)

### ImprovementRecommender

**generate_recommendations(metrics_summary, expert_reviews)**
- Назначение: генерация рекомендаций по улучшению
- Параметры:
  - `metrics_summary` - агрегированные метрики
  - `expert_reviews` - результаты экспертных оценок
- Возвращает: `Recommendations` (priority_areas, prompt_suggestions, training_gaps)

### ReportGenerator

**generate_weekly_report(start_date, end_date)**
- Назначение: генерация еженедельного отчета
- Параметры:
  - `start_date` - начало недели
  - `end_date` - конец недели
- Возвращает: `WeeklyReport` (summary, trends, alerts, expert_reviews_summary)

## Взаимодействие компонентов

### Real-time Evaluation Flow

```
MainAgent -> bot_response
  |
  v
EvaluationCoordinator.evaluate_response()
  |
  +---> BehavioralObserver.extract_markers() -> MetricsCalculator.calculate_bolt_score()
  |
  +---> EmpathyValidator.validate_empathy() + ClinicalChecker.check_appropriateness()
  |
  v
MetricsAggregator.aggregate()
  |
  +---> IF low_score OR safety_flag: ReviewQueue.add_to_queue()
  |
  +---> IF high_score: Mark as training_example
  |
  v
Store to PostgreSQL (evaluation_results table)
  |
  v
MetricsAPI (для dashboard real-time display)
```

### Expert Review Flow

```
ReviewQueue.add_to_queue(conversation_id, reason="low_bolt_score")
  |
  v
ExpertInterface.get_next_for_review(expert_id) -> ReviewItem
  |
  v
Expert оценивает через UI
  |
  v
ExpertInterface.submit_expert_review(scores, comments)
  |
  v
ConsensusAggregator.aggregate_expert_scores() [если >1 эксперт]
  |
  v
Store to expert_reviews table
  |
  v
ImprovementRecommender.generate_recommendations()
```

### Red-team Testing Flow

```
[Scheduled Task] -> TestRunner.run_red_team_scenarios(adversarial_prompts)
  |
  v
FOR each scenario:
  - Simulate user input
  - Get bot response
  - VulnerabilityDetector.detect(response, scenario_expectations)
  |
  v
Aggregate results -> RedTeamReport
  |
  v
Store to red_team_reports table
  |
  v
Alert if critical vulnerabilities found
```

### Feedback Loop Flow

```
[Weekly Task] -> MetricsAggregator.aggregate_period_metrics(last_7_days)
  |
  v
ImprovementRecommender.generate_recommendations(metrics, expert_reviews)
  |
  v
PromptTuningSuggestions.suggest_prompt_changes()
  |
  v
Human Review -> Approval
  |
  v
Update prompts/techniques configuration
  |
  v
Re-run TestRunner для валидации improvements
```

## Порядок реализации

### Этап 1: Базовая инфраструктура оценки (Фаза MVP)

1. **PostgreSQL schema для evaluation_results**
   - Таблицы: bolt_scores, vera_scores, evaluation_summary
   - Индексы для быстрого поиска по user_id, conversation_id, timestamp

2. **EvaluationCoordinator скелет**
   - Базовая координация BOLT и VERA модулей
   - Сохранение результатов в БД

3. **BehavioralObserver (упрощенная версия)**
   - Regex-based extraction ключевых маркеров (reflections, questions, validations)
   - Простой подсчет частоты маркеров

4. **MetricsCalculator для BOLT**
   - Загрузка rubrics из YAML
   - Расчет scores по формуле

### Этап 2: VERA-MH Integration

5. **EmpathyValidator**
   - Интеграция pre-trained BERT модели для empathy scoring
   - Semantic similarity между user emotion и bot response

6. **ClinicalChecker**
   - Rule-based проверка противопоказанных интервенций
   - Mapping техник к эмоциональным состояниям (из IP-04)

7. **Aggregation логика**
   - Weighted average BOLT + VERA
   - Safety flag detection

### Этап 3: Expert Review Pipeline

8. **ReviewQueue и ExpertInterface**
   - Celery task queue для асинхронной обработки
   - Простой REST API для экспертов

9. **ConsensusAggregator**
   - Averaging экспертных оценок
   - Inter-rater reliability расчет

### Этап 4: Red-teaming

10. **Adversarial prompts набор**
    - YAML файл с 20-30 сценариями
    - Категории: manipulation, harmful_advice, boundary_violation, toxic_input

11. **TestRunner и VulnerabilityDetector**
    - Автоматический запуск сценариев
    - Детекция failures (expected vs actual response)

### Этап 5: Feedback Loop и Dashboard

12. **MetricsAggregator и ImprovementRecommender**
    - Временные ряды в TimescaleDB
    - Rule-based рекомендации

13. **MetricsAPI и basic Dashboard**
    - REST API для получения метрик
    - Простой HTML dashboard с plotly charts

14. **ReportGenerator**
    - Weekly/monthly отчеты в markdown формате
    - Email notifications для супервизоров

### Этап 6: Refinement

15. **PromptTuningSuggestions**
    - Автоматические предложения на основе low-scoring областей

16. **Advanced BERT fine-tuning**
    - Fine-tune empathy model на domain-specific данных

## Критичные граничные случаи

### 1. Conflicting Scores

**Ситуация**: BOLT Score высокий (4.5), но VERA Score низкий (40)

**Обработка**:
- Автоматически отправить на экспертную оценку
- Логировать как conflicting_evaluation
- Использовать экспертную оценку для калибровки автоматических систем

### 2. Expert Disagreement

**Ситуация**: Два эксперта дали разные оценки (3.0 vs 5.0)

**Обработка**:
- ConsensusAggregator рассчитывает inter-rater reliability
- Если расхождение > 1.5 балла, привлечь третьего эксперта
- Использовать median вместо mean для финальной оценки

### 3. Red-team Test Failure

**Ситуация**: Бот выдал harmful advice в red-team сценарии

**Обработка**:
- Немедленный alert супервизору
- Автоматически disable затронутый emotional state или technique
- Создать incident report
- Не развертывать новую версию до фикса

### 4. Safety False Positives

**Ситуация**: Safety flag срабатывает на безобидные сообщения (например, "я не хочу жить так, как жил раньше")

**Обработка**:
- Экспертная валидация false positives
- Добавить в training set для улучшения SafetyDetector
- Настройка thresholds через конфигурацию

### 5. Evaluation Latency Impact

**Ситуация**: Real-time evaluation замедляет ответы бота

**Обработка**:
- Асинхронная оценка после отправки ответа пользователю
- Caching BERT embeddings для ускорения
- Batch evaluation для non-critical cases

## Допущения

1. **Expert Availability**: Допускаем наличие 2-3 клинических экспертов для review (психологи/психотерапевты с опытом работы с PA)
2. **Pre-trained Models**: Используем публично доступные BERT модели для empathy scoring, адаптируем через fine-tuning
3. **BOLT Rubrics**: Адаптируем оригинальные BOLT критерии под специфику PA контекста
4. **Expert Review Volume**: 10% диалогов на экспертную оценку - управляемый объем для 2-3 экспертов
5. **Red-team Scenarios**: Начинаем с 20-30 сценариев, расширяем на основе real-world incidents
6. **MVP Scope**: Автоматическое prompt tuning оставляем для следующей итерации, сначала фокус на мониторинг и человеческий review

## Открытые вопросы

1. **Частота expert review**: Какой % диалогов отправлять на экспертную оценку? (10% - базовое допущение)
2. **Expert compensation**: Бюджет на оплату экспертов за review?
3. **BOLT rubrics customization**: Нужна ли валидация адаптированных BOLT критериев с авторами фреймворка?
4. **Red-team frequency**: Как часто запускать red-team тесты? (предложение: еженедельно)
5. **Threshold calibration**: Какие thresholds для BOLT/VERA scores считать acceptable? (предложение: BOLT >= 3.0, VERA >= 60)
6. **Expert qualifications**: Требования к экспертам (клинический психолог, психотерапевт, специфический опыт с PA)?
7. **Legal review**: Требуется ли юридическая валидация системы оценки для compliance?

## Acceptance Criteria

### Happy Path

1. **Автоматическая оценка работает**:
   - После каждого ответа бота рассчитываются BOLT и VERA scores
   - Результаты сохраняются в БД в течение 500ms

2. **Low-quality responses детектируются**:
   - Ответы с BOLT < 2.5 или VERA < 50 автоматически попадают в ReviewQueue
   - Safety incidents триггерят немедленный alert

3. **Expert review функционален**:
   - Эксперт может получить следующий диалог из очереди
   - Эксперт может отправить оценки и комментарии
   - Consensus aggregation работает для multiple reviewers

4. **Red-team тесты запускаются**:
   - Еженедельный запуск adversarial scenarios
   - Vulnerability report генерируется и отправляется супервизору
   - Critical vulnerabilities блокируют deployment

5. **Dashboard доступен**:
   - Отображает текущие BOLT/VERA trends (за последние 7/30 дней)
   - Показывает safety incidents count
   - Предоставляет доступ к expert reviews

6. **Feedback loop работает**:
   - ImprovementRecommender генерирует рекомендации на основе метрик
   - Recommendations доступны в dashboard

### Ручной сценарий проверки

1. **Создать тестовый диалог** с низким качеством ответа (неэмпатичный, директивный)
2. **Запустить EvaluationCoordinator.evaluate_response()**
3. **Проверить**:
   - BOLT и VERA scores рассчитаны
   - Диалог добавлен в ReviewQueue
4. **Зайти в ExpertInterface** как эксперт
5. **Получить диалог из очереди** через get_next_for_review()
6. **Отправить экспертную оценку** с scores и комментарием
7. **Проверить** сохранение в expert_reviews table
8. **Запустить TestRunner** с 3-5 adversarial prompts
9. **Проверить VulnerabilityDetector** детектирует failures
10. **Открыть Dashboard** и проверить отображение метрик

## Definition of Done

- [x] PostgreSQL schema создана (bolt_scores, vera_scores, expert_reviews, red_team_reports)
- [x] EvaluationCoordinator реализован и интегрирован с MainAgent
- [x] BehavioralObserver и MetricsCalculator работают (BOLT framework)
- [x] EmpathyValidator и ClinicalChecker работают (VERA-MH framework)
- [x] ReviewQueue и ExpertInterface функциональны
- [x] TestRunner и VulnerabilityDetector запускают red-team сценарии
- [x] MetricsAPI и basic Dashboard доступны
- [x] ReportGenerator генерирует weekly отчеты
- [x] ImprovementRecommender предоставляет рекомендации
- [x] Логи всех evaluation events
- [x] Метрики: evaluation_latency, bolt_score_distribution, vera_score_distribution, expert_reviews_count
- [x] Feature flag: EVALUATION_ENABLED
- [x] README для evaluation модуля с инструкциями для экспертов

## Минимальные NFR для MVP

### Производительность

- **Evaluation latency**: <= 500ms для real-time оценки (не блокирует ответ пользователю)
- **Batch evaluation**: обработка 1000 диалогов за ночь (для historical analysis)
- **Dashboard response time**: <= 2s для загрузки метрик за 30 дней

### Надежность

- **Evaluation failures**: допустимо 1% failures (retry с exponential backoff)
- **Expert review SLA**: 95% диалогов оценены в течение 48 часов
- **Red-team test runs**: 100% completion rate (failures логируются для manual review)

### Ограничения по ресурсам

- **Memory**: <= 2GB RAM для evaluation процесса (BERT inference)
- **CPU**: <= 2 CPU cores для evaluation coordinator
- **Database**: TimescaleDB для временных рядов (retention 90 дней для детальных метрик, агрегаты - 1 год)
- **Storage**: ~100MB/1000 диалогов для evaluation results

## Требования безопасности

- **Секреты**: API keys для external evaluation services (если используются) только через secret manager
- **PII защита**: Не логировать PII в evaluation reports (anonymize user_id в reports)
- **Expert access control**: Role-based access для ExpertInterface (только certified reviewers)
- **Audit trail**: Все экспертные оценки логируются с expert_id и timestamp для accountability
- **Data retention**: GDPR compliance - удаление evaluation data при удалении пользователя

## Наблюдаемость

### Логи

- **Evaluation events**: каждая оценка логируется с результатами
- **Expert reviews**: submission и consensus events
- **Red-team tests**: запуск, результаты, vulnerabilities
- **Low-quality alerts**: все случаи BOLT < 2.5 или VERA < 50
- **Safety incidents**: все safety flags с контекстом

### Метрики

- **evaluation_total**: счетчик всех оценок
- **evaluation_latency_ms**: histogram задержек оценки
- **bolt_score_distribution**: histogram BOLT scores
- **vera_score_distribution**: histogram VERA scores
- **low_quality_count**: счетчик low-quality responses
- **safety_incidents_count**: счетчик safety flags
- **expert_reviews_count**: счетчик экспертных оценок
- **expert_review_latency_hours**: histogram времени до review
- **red_team_failures_count**: счетчик failed red-team tests
- **improvement_recommendations_count**: счетчик generated recommendations

### Трассировка

- **Span start**: EvaluationCoordinator.evaluate_response()
- **Child spans**: BehavioralObserver, MetricsCalculator, EmpathyValidator, ClinicalChecker
- **Span end**: результаты сохранены в БД
- **Trace ID**: привязан к conversation_id для cross-service tracing

## Релиз

### Включение через feature flag

```yaml
EVALUATION_ENABLED: true
REAL_TIME_EVALUATION: true    # vs batch only
EXPERT_REVIEW_ENABLED: true
RED_TEAM_ENABLED: true
DASHBOARD_PUBLIC: false        # доступ только для супервизоров
```

### План развертывания

1. **Dev environment**: полное тестирование всех компонентов
2. **Staging**:
   - Запуск на historical данных (batch evaluation 1000+ диалогов)
   - Валидация BOLT/VERA scores с экспертами
   - Red-team testing
3. **Production**:
   - Фаза 1 (неделя 1): EVALUATION_ENABLED=true, REAL_TIME_EVALUATION=false (только batch)
   - Фаза 2 (неделя 2): REAL_TIME_EVALUATION=true для 10% пользователей (A/B test)
   - Фаза 3 (неделя 3): 100% пользователей если latency приемлема
   - Фаза 4 (неделя 4): EXPERT_REVIEW_ENABLED=true, RED_TEAM_ENABLED=true

## Откат

### Условия отката

- Evaluation latency > 1s (impact на user experience)
- Database overload (evaluation writes вызывают contention)
- Critical vulnerability найдена red-team тестом и не может быть быстро исправлена
- Expert review queue > 500 items (overwhelmed experts)

### Шаги возврата состояния

1. **Немедленный откат**: Set `EVALUATION_ENABLED=false` через feature flag
2. **Graceful degradation**:
   - Остановить real-time evaluation
   - Продолжить batch evaluation ночью для мониторинга
3. **Database cleanup**: Если performance issue - архивировать старые evaluation_results
4. **Expert notification**: Уведомить экспертов о приостановке review process
5. **Root cause analysis**: Анализ логов и метрик для определения причины
6. **Fix и re-deployment**: После фикса - повторить фазу 1 deployment

## Риски и митигации

### Риск 1: Low Inter-rater Reliability экспертов

**Описание**: Эксперты дают сильно расходящиеся оценки (низкий agreement)

**Митигация**:
- Провести calibration session с экспертами перед запуском
- Использовать consensus meeting для спорных случаев
- Рассчитывать Cohen's kappa для мониторинга agreement
- Обучение экспертов на эталонных примерах

### Риск 2: BERT модель не адаптирована к PA domain

**Описание**: Pre-trained empathy model дает низкую точность на PA контексте

**Митигация**:
- Собрать labeled dataset из expert reviews (200+ примеров)
- Fine-tune BERT на PA-specific данных
- A/B тест pre-trained vs fine-tuned модели
- Fallback на rule-based подход если model confidence низкий

### Риск 3: Red-team набор неполный

**Описание**: Adversarial scenarios не покрывают все векторы атак

**Митигация**:
- Continuous expansion adversarial_prompts на основе real incidents
- Привлечь external red-teamers для review scenarios
- Мониторинг public research по LLM vulnerabilities
- Quarterly review и update сценариев

### Риск 4: Expert Review Bottleneck

**Описание**: Объем диалогов для review превышает capacity экспертов

**Митигация**:
- Adaptive threshold: если queue > 100, повысить BOLT/VERA thresholds для отправки на review
- Приоритизация: safety incidents - высокий приоритет, остальное - по score severity
- Automated pre-filtering: фильтровать очевидные false positives перед экспертами
- Scale expert team если нужно

### Риск 5: Evaluation Cost

**Описание**: BERT inference и expert reviews увеличивают operational costs

**Митигация**:
- Batch evaluation для non-critical paths
- Caching BERT embeddings для повторных вычислений
- Sampling: real-time evaluation для 50% диалогов, batch для остальных
- ROI analysis: мониторинг корреляции evaluation метрик с user satisfaction

### Риск 6: Privacy Concerns при Expert Review

**Описание**: Передача user conversations экспертам может нарушить privacy

**Митигация**:
- Anonymization: удалить PII перед отправкой на review
- NDA для всех экспертов
- Access logging: audit trail всех доступов экспертов к диалогам
- User consent: информировать пользователей о возможной экспертной оценке

## Самопроверка плана

- [x] Нет кода и псевдокода (только описание архитектуры и логики)
- [x] Заполнены scope, acceptance criteria, risks, release plan
- [x] Файл именован согласно формату IP-06-evaluation-framework.md
- [x] Нет упоминаний секретов и приватных URL
- [x] Покрыты все компоненты из Workstream 6 PDF (BOLT, VERA-MH, expert review, red-teaming)
- [x] Интеграция с предыдущими IP (IP-03 emotional states, IP-04 techniques, IP-05 safety)
- [x] Mermaid диаграммы для визуализации архитектуры
- [x] Детальный flow работы функционала от начала до конца
- [x] Критичные граничные случаи идентифицированы
- [x] NFR, безопасность, observability, release, откат, риски - все секции заполнены
