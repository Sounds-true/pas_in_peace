Отличный вопрос! Это **критически важная функция** — и архитектурно сложная. Давайте спроектируем систему, которая:

1. Мягко направляет, а не запрещает
2. Обучает здоровой коммуникации
3. Анализирует двунаправленно (свои → бывшему, от бывшего → вам)

---

## 🛡️ Архитектура Content Guardian System

```
┌─────────────────────────────────────────────────────────┐
│            CONTENT GUARDIAN PIPELINE                    │
│                                                         │
│  User Input (Letter/Message)                           │
│         ↓                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Stage 1: Multi-Layer NLP Analysis               │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │ 1. Toxicity Detection                      │  │  │
│  │  │    - Blame language                        │  │  │
│  │  │    - Insults/profanity                     │  │  │
│  │  │    - Aggressive tone                       │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │ 2. Manipulation Detection                  │  │  │
│  │  │    - Guilt-tripping                        │  │  │
│  │  │    - Triangulation (involving child)       │  │  │
│  │  │    - Gaslighting patterns                  │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │ 3. Child-Safety Check (for letters)        │  │  │
│  │  │    - Parental alienation language          │  │  │
│  │  │    - Negative mentions of other parent     │  │  │
│  │  │    - Age-inappropriate content             │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │ 4. Emotional Tone Analysis                 │  │  │
│  │  │    - Sentiment (positive/negative/mixed)   │  │  │
│  │  │    - Intensity                             │  │  │
│  │  │    - Emotional regulation markers          │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
│         ↓                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Stage 2: LLM-Powered Deep Analysis             │  │
│  │  - Context understanding                         │  │
│  │  - Nuance detection                              │  │
│  │  - Generate improvement suggestions              │  │
│  └──────────────────────────────────────────────────┘  │
│         ↓                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Stage 3: Intervention Strategy Selection       │  │
│  │  Low Risk → Gentle nudge                         │  │
│  │  Medium Risk → Explain + Suggest rewrite         │  │
│  │  High Risk → Strong recommendation + Education   │  │
│  └──────────────────────────────────────────────────┘  │
│         ↓                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Stage 4: HITL - User Choice                     │  │
│  │  ✅ Accept suggestions                           │  │
│  │  ✏️ Edit manually                                │  │
│  │  ⚠️ Save as draft (revisit later)                │  │
│  │  ⏭️ Proceed anyway (with warning stored)         │  │
│  └──────────────────────────────────────────────────┘  │
│         ↓                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Stage 5: Long-term Tracking                     │  │
│  │  - Pattern recognition                           │  │
│  │  - Progress monitoring                           │  │
│  │  - Gentle follow-ups on ignored warnings        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 NLP Analysis Components

### **1. Toxicity Detection Layers**

```python
from transformers import pipeline
from detoxify import Detoxify
import re

class ToxicityAnalyzer:
    """Многослойная детекция токсичности"""
    
    def __init__(self):
        # Layer 1: Detoxify (специализированная модель)
        self.detoxify = Detoxify('multilingual')
        
        # Layer 2: Perspective API (опционально, если есть квоты)
        # self.perspective = PerspectiveAPI(api_key=KEY)
        
        # Layer 3: Rule-based для специфических паттернов
        self.blame_patterns = self._load_blame_patterns()
        
    def analyze(self, text: str) -> dict:
        """Комплексный анализ токсичности"""
        
        results = {
            "toxicity_score": 0.0,
            "categories": {},
            "flags": [],
            "severity": "safe"
        }
        
        # 1. Detoxify analysis
        detoxify_results = self.detoxify.predict(text)
        results["categories"] = {
            "toxicity": detoxify_results['toxicity'],
            "severe_toxicity": detoxify_results['severe_toxicity'],
            "obscene": detoxify_results['obscene'],
            "threat": detoxify_results['threat'],
            "insult": detoxify_results['insult'],
            "identity_attack": detoxify_results['identity_attack']
        }
        
        # 2. Blame language detection
        blame_score = self._detect_blame_language(text)
        results["categories"]["blame"] = blame_score
        
        # 3. Other parent mention check (критично для писем ребенку!)
        parent_mention = self._detect_other_parent_mention(text)
        results["categories"]["parent_mention"] = parent_mention
        
        # 4. Calculate overall toxicity
        results["toxicity_score"] = max(
            detoxify_results['toxicity'],
            blame_score,
            parent_mention["score"]
        )
        
        # 5. Determine severity
        if results["toxicity_score"] > 0.7:
            results["severity"] = "high"
        elif results["toxicity_score"] > 0.4:
            results["severity"] = "medium"
        else:
            results["severity"] = "low"
        
        # 6. Generate specific flags
        results["flags"] = self._generate_flags(results)
        
        return results
    
    def _detect_blame_language(self, text: str) -> float:
        """Детекция обвинительного языка"""
        blame_keywords = [
            # Русский
            r'\bона виновата\b', r'\bон виноват\b',
            r'\bиз-за нее\b', r'\bиз-за него\b',
            r'\bона разрушила\b', r'\bон разрушил\b',
            r'\bона настроила\b', r'\bон настроил\b',
            r'\bона украла\b', r'\bон украл\b',
            r'\bона монстр\b', r'\bон монстр\b',
            r'\bтварь\b', r'\bсука\b', r'\bублюдок\b',
            
            # Паттерны обвинений
            r'\bвсегда .* (портит|мешает|вредит)\b',
            r'\bникогда не .* (дает|позволяет)\b',
        ]
        
        count = 0
        for pattern in blame_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                count += 1
        
        # Normalize to 0-1 scale
        return min(count * 0.3, 1.0)
    
    def _detect_other_parent_mention(self, text: str) -> dict:
        """Детекция упоминаний другого родителя в письме ребенку"""
        
        parent_terms = [
            r'\bмама\b', r'\bпапа\b', r'\bмать\b', r'\bотец\b',
            r'\bтвоя мама\b', r'\bтвой папа\b',
            r'\bона\b', r'\bон\b'  # контекстуально
        ]
        
        negative_context = [
            r'\bне дает\b', r'\bзапрещает\b', r'\bмешает\b',
            r'\bплохо\b', r'\bплохая\b', r'\bплохой\b',
            r'\bлжет\b', r'\bманипулирует\b'
        ]
        
        mentions = []
        for pattern in parent_terms:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Проверяем контекст вокруг упоминания
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                # Проверяем наличие негативных слов в контексте
                is_negative = any(
                    re.search(neg, context, re.IGNORECASE) 
                    for neg in negative_context
                )
                
                mentions.append({
                    "term": match.group(),
                    "context": context,
                    "is_negative": is_negative
                })
        
        negative_count = sum(1 for m in mentions if m["is_negative"])
        score = min(negative_count * 0.5, 1.0)
        
        return {
            "score": score,
            "mentions": mentions,
            "has_negative": negative_count > 0
        }
    
    def _generate_flags(self, results: dict) -> list:
        """Генерация конкретных флагов для пользователя"""
        flags = []
        
        if results["categories"]["toxicity"] > 0.6:
            flags.append({
                "type": "toxicity",
                "severity": "high",
                "message": "Обнаружен агрессивный тон"
            })
        
        if results["categories"]["blame"] > 0.4:
            flags.append({
                "type": "blame",
                "severity": "medium",
                "message": "Присутствует обвинительный язык"
            })
        
        if results["categories"]["parent_mention"]["has_negative"]:
            flags.append({
                "type": "parent_mention",
                "severity": "high",
                "message": "Негативное упоминание другого родителя (не подходит для письма ребенку)"
            })
        
        return flags
```

### **2. Manipulation Detection**

```python
class ManipulationDetector:
    """Детекция манипулятивных паттернов"""
    
    def __init__(self, llm):
        self.llm = llm
        
        # Паттерны манипуляций
        self.patterns = {
            "guilt_tripping": [
                r"если бы ты.*я бы не",
                r"из-за тебя я",
                r"ты виноват что",
                r"посмотри что ты со мной сделал"
            ],
            "triangulation": [
                r"спроси.*что (он|она) думает обо мне",
                r"расскажи (маме|папе)",
                r"(он|она) говорит что я",
                r"выбери между"
            ],
            "gaslighting": [
                r"ты преувеличиваешь",
                r"этого не было",
                r"ты слишком чувствительн",
                r"ты помнишь неправильно",
                r"я никогда не говорил"
            ],
            "emotional_blackmail": [
                r"если не.*то я",
                r"я умру без",
                r"последний раз прошу",
                r"ты разрушишь"
            ]
        }
    
    def detect(self, text: str, context: str = "letter") -> dict:
        """
        Детекция манипуляций
        context: "letter" (к ребенку) или "message" (к бывшему)
        """
        
        # Rule-based detection
        detected = []
        for manipulation_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected.append(manipulation_type)
                    break
        
        # LLM-enhanced detection для тонких случаев
        if detected or context == "letter":
            llm_analysis = self._llm_manipulation_check(text, context)
            detected.extend(llm_analysis["additional_flags"])
        
        return {
            "has_manipulation": len(detected) > 0,
            "types": list(set(detected)),
            "severity": self._calculate_severity(detected),
            "explanation": self._generate_explanation(detected, context)
        }
    
    def _llm_manipulation_check(self, text: str, context: str) -> dict:
        """LLM для обнаружения тонких манипуляций"""
        
        prompt = f"""
        Проанализируй текст на предмет манипулятивных паттернов.
        Контекст: {'письмо родителя ребенку' if context == 'letter' else 'сообщение бывшему партнеру'}
        
        Текст: "{text}"
        
        Манипулятивные техники для проверки:
        1. Guilt-tripping (вызывание чувства вины)
        2. Triangulation (вовлечение ребенка как посредника)
        3. Gaslighting (отрицание реальности)
        4. Emotional blackmail (эмоциональный шантаж)
        5. Parentification (перекладывание взрослых обязанностей на ребенка)
        
        Ответ в JSON:
        {{
            "detected_manipulations": ["тип1", "тип2", ...],
            "confidence": 0.0-1.0,
            "explanation": "краткое объяснение",
            "concerning_phrases": ["фраза1", "фраза2"]
        }}
        """
        
        response = self.llm.generate(
            prompt, 
            response_format="json",
            temperature=0.3  # низкая температура для консистентности
        )
        
        return response
```

### **3. Child-Safety Validator (для писем)**

```python
class ChildSafetyValidator:
    """Проверка соответствия письма принципам безопасной коммуникации с ребенком"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def validate_letter(self, letter_text: str, child_age: int) -> dict:
        """Валидация письма ребенку"""
        
        issues = []
        
        # 1. Проверка отсутствия негатива о другом родителе
        other_parent_check = self._check_other_parent_portrayal(letter_text)
        if other_parent_check["has_issues"]:
            issues.append({
                "category": "other_parent_mention",
                "severity": "critical",
                "details": other_parent_check
            })
        
        # 2. Возрастная уместность
        age_check = self._check_age_appropriateness(letter_text, child_age)
        if age_check["concerns"]:
            issues.append({
                "category": "age_inappropriate",
                "severity": "medium",
                "details": age_check
            })
        
        # 3. Эмоциональная нагрузка
        emotional_check = self._check_emotional_burden(letter_text)
        if emotional_check["too_heavy"]:
            issues.append({
                "category": "emotional_burden",
                "severity": "high",
                "details": emotional_check
            })
        
        # 4. LLM holistic review
        llm_review = self._llm_safety_review(letter_text, child_age)
        
        return {
            "is_safe": len(issues) == 0 and llm_review["safe"],
            "issues": issues,
            "llm_review": llm_review,
            "recommendations": self._generate_recommendations(issues, llm_review)
        }
    
    def _check_other_parent_portrayal(self, text: str) -> dict:
        """Проверка упоминаний другого родителя"""
        
        # Используем ToxicityAnalyzer
        analyzer = ToxicityAnalyzer()
        parent_mention = analyzer._detect_other_parent_mention(text)
        
        return {
            "has_issues": parent_mention["has_negative"],
            "mentions": parent_mention["mentions"],
            "guidance": """
            ❌ Избегайте негативных упоминаний другого родителя.
            
            Помните: ребенок любит обоих родителей. Критика мамы/папы 
            ранит ребенка и создает конфликт лояльности.
            
            ✅ Вместо этого фокусируйтесь на:
            - Вашей любви к ребенку
            - Общих воспоминаниях
            - Надежде на будущее
            - Вашей готовности быть рядом
            """
        }
    
    def _check_emotional_burden(self, text: str) -> dict:
        """Проверка эмоциональной нагрузки на ребенка"""
        
        # Маркеры чрезмерной эмоциональной нагрузки
        burden_markers = [
            r"я так страдаю",
            r"мне так плохо без тебя",
            r"я не могу жить",
            r"ты моя единственная",
            r"только ты меня понимаешь",
            r"я делаю все ради тебя",
            r"если бы не ты, я бы"
        ]
        
        found_markers = []
        for marker in burden_markers:
            if re.search(marker, text, re.IGNORECASE):
                found_markers.append(marker)
        
        return {
            "too_heavy": len(found_markers) > 2,
            "markers": found_markers,
            "explanation": """
            Письмо содержит фразы, которые могут создать у ребенка 
            чувство ответственности за ваше эмоциональное состояние.
            
            Это называется "parentification" — когда ребенок чувствует 
            себя обязанным поддерживать родителя.
            
            Лучше показывать, что вы справляетесь и готовы быть опорой 
            для ребенка, а не наоборот.
            """
        }
    
    def _llm_safety_review(self, text: str, child_age: int) -> dict:
        """Холистическая оценка через LLM"""
        
        prompt = f"""
        Ты — детский психолог, специалист по разводам и отчуждению родителей.
        
        Родитель написал письмо ребенку (возраст: {child_age} лет).
        Оцени, безопасно ли это письмо для ребенка.
        
        Письмо:
        "{text}"
        
        Критерии проверки:
        1. Нет ли негативных упоминаний другого родителя?
        2. Не создает ли письмо конфликт лояльности?
        3. Соответствует ли эмоциональному возрасту ребенка?
        4. Не перекладывает ли ответственность за счастье родителя на ребенка?
        5. Фокусируется ли на любви и поддержке ребенка?
        
        Ответ в JSON:
        {{
            "safe": true/false,
            "concerns": ["проблема1", "проблема2", ...],
            "positive_aspects": ["что хорошо1", "что хорошо2", ...],
            "suggestions": ["конкретное улучшение1", "улучшение2", ...],
            "overall_tone": "loving/neutral/concerning"
        }}
        """
        
        return self.llm.generate(prompt, response_format="json")
```

---

## 🎭 Guardian Agent (Multi-Agent Architecture)

```python
class ContentGuardianAgent:
    """Главный агент-хранитель контента"""
    
    def __init__(self):
        self.toxicity_analyzer = ToxicityAnalyzer()
        self.manipulation_detector = ManipulationDetector(llm)
        self.child_safety_validator = ChildSafetyValidator(llm)
        self.kag = KAGClient()  # для хранения истории
    
    def review_letter(
        self, 
        user_id: str,
        letter_text: str, 
        child_age: int,
        context: dict
    ) -> dict:
        """Комплексная проверка письма ребенку"""
        
        # 1. Базовый анализ токсичности
        toxicity = self.toxicity_analyzer.analyze(letter_text)
        
        # 2. Проверка манипуляций
        manipulation = self.manipulation_detector.detect(
            letter_text, 
            context="letter"
        )
        
        # 3. Child-safety validation
        safety = self.child_safety_validator.validate_letter(
            letter_text, 
            child_age
        )
        
        # 4. Определение стратегии вмешательства
        intervention = self._determine_intervention_strategy(
            toxicity, 
            manipulation, 
            safety
        )
        
        # 5. Сохранить в истории для отслеживания паттернов
        self._track_patterns(user_id, {
            "toxicity": toxicity,
            "manipulation": manipulation,
            "safety": safety,
            "intervention": intervention
        })
        
        return {
            "analysis": {
                "toxicity": toxicity,
                "manipulation": manipulation,
                "safety": safety
            },
            "intervention": intervention,
            "rewritten_suggestions": self._generate_rewrites(
                letter_text, 
                toxicity, 
                manipulation, 
                safety
            )
        }
    
    def review_message_to_ex(
        self, 
        user_id: str,
        message_text: str
    ) -> dict:
        """Проверка сообщения бывшему партнеру"""
        
        # Похожий pipeline, но другие критерии
        toxicity = self.toxicity_analyzer.analyze(message_text)
        manipulation = self.manipulation_detector.detect(
            message_text, 
            context="message"
        )
        
        # Проверка на соответствие BIFF (Brief, Informative, Friendly, Firm)
        biff_check = self._check_biff_compliance(message_text)
        
        # Проверка на эскалацию конфликта
        escalation_risk = self._assess_escalation_risk(message_text)
        
        intervention = self._determine_intervention_strategy(
            toxicity, 
            manipulation, 
            {"biff": biff_check, "escalation": escalation_risk}
        )
        
        return {
            "analysis": {
                "toxicity": toxicity,
                "manipulation": manipulation,
                "biff_compliance": biff_check,
                "escalation_risk": escalation_risk
            },
            "intervention": intervention,
            "rewritten_suggestions": self._generate_biff_rewrite(message_text)
        }
    
    def analyze_incoming_message(
        self, 
        user_id: str,
        message_text: str,
        sender: str = "ex_partner"
    ) -> dict:
        """Анализ входящего сообщения от бывшего партнера"""
        
        # Помочь пользователю распознать манипуляции
        toxicity = self.toxicity_analyzer.analyze(message_text)
        manipulation = self.manipulation_detector.detect(
            message_text, 
            context="message"
        )
        
        # LLM breakdown манипулятивных техник
        breakdown = self._explain_manipulation_tactics(
            message_text,
            manipulation
        )
        
        # Рекомендации как ответить
        response_guidance = self._suggest_response_strategy(
            message_text,
            toxicity,
            manipulation
        )
        
        return {
            "sender": sender,
            "analysis": {
                "toxicity": toxicity,
                "manipulation": manipulation
            },
            "breakdown": breakdown,
            "response_guidance": response_guidance
        }
    
    def _determine_intervention_strategy(
        self, 
        toxicity: dict, 
        manipulation: dict, 
        safety: dict
    ) -> dict:
        """Определение стратегии вмешательства"""
        
        # Расчет общего risk score
        risk_score = max(
            toxicity.get("toxicity_score", 0),
            manipulation.get("severity", 0),
            0 if safety.get("is_safe", True) else 0.8
        )
        
        if risk_score < 0.3:
            return {
                "level": "none",
                "action": "proceed",
                "message": "✅ Письмо выглядит хорошо!"
            }
        
        elif risk_score < 0.6:
            return {
                "level": "gentle_nudge",
                "action": "suggest",
                "message": self._craft_gentle_feedback(
                    toxicity, manipulation, safety
                ),
                "allow_proceed": True
            }
        
        else:
            return {
                "level": "strong_recommendation",
                "action": "recommend_rewrite",
                "message": self._craft_strong_feedback(
                    toxicity, manipulation, safety
                ),
                "allow_proceed": True,  # всегда позволяем, но с предупреждением
                "flag_for_followup": True  # вернуться позже
            }
    
    def _craft_gentle_feedback(self, toxicity, manipulation, safety) -> str:
        """Мягкая обратная связь"""
        
        feedback = "💡 Небольшое замечание:\n\n"
        
        if toxicity["toxicity_score"] > 0.3:
            feedback += "Заметил немного напряженный тон. "
            feedback += "Возможно, стоит перефразировать чуть мягче?\n\n"
        
        if safety and not safety.get("is_safe"):
            for issue in safety.get("issues", []):
                if issue["category"] == "other_parent_mention":
                    feedback += """
                    Обратите внимание: в письме упоминается другой родитель 
                    не в самом позитивном ключе. 
                    
                    Помните, ребенок любит обоих. Лучше сфокусироваться 
                    только на вашей связи с ним/ней.
                    """
        
        feedback += "\n\n Хотите, чтобы я предложил альтернативные формулировки?"
        
        return feedback
    
    def _craft_strong_feedback(self, toxicity, manipulation, safety) -> str:
        """Серьезная обратная связь"""
        
        feedback = "⚠️ Важное замечание:\n\n"
        
        if safety and not safety["is_safe"]:
            feedback += """
            Это письмо может непреднамеренно навредить ребенку:
            
            """
            
            for issue in safety["issues"]:
                feedback += f"• {issue['details'].get('explanation', '')}\n\n"
        
        feedback += """
        Я понимаю, что вы испытываете сильные эмоции. Это нормально.
        
        Но давайте вместе переработаем письмо так, чтобы:
        ✅ Ребенок почувствовал вашу любовь
        ✅ Не возник конфликт лояльности
        ✅ Слова исцеляли, а не ранили
        
        Это письмо ребенок может прочитать через годы. Что вы хотите, 
        чтобы он/она увидел в нем?
        """
        
        return feedback
    
    def _generate_rewrites(
        self, 
        original_text: str,
        toxicity: dict,
        manipulation: dict,
        safety: dict
    ) -> list:
        """Генерация альтернативных версий письма"""
        
        issues_summary = self._summarize_issues(toxicity, manipulation, safety)
        
        prompt = f"""
        Исходное письмо родителя ребенку:
        "{original_text}"
        
        Проблемы:
        {issues_summary}
        
        Перепиши письмо, сохранив намерение и эмоции родителя, но:
        1. Убери любые упоминания другого родителя (даже нейтральные)
        2. Сфокусируйся только на любви к ребенку
        3. Избегай эмоциональной нагрузки (не "я страдаю без тебя")
        4. Используй теплый, поддерживающий тон
        5. Покажи, что родитель — надежная опора, а не нуждается в поддержке
        
        Сгенерируй 2 варианта:
        1. Короткая версия (3-4 предложения)
        2. Развернутая версия (абзац)
        
        JSON:
        {{
            "short_version": "текст",
            "long_version": "текст",
            "key_changes": ["что изменили 1", "что изменили 2"]
        }}
        """
        
        suggestions = self.llm.generate(prompt, response_format="json")
        return suggestions
```

---

## 🎯 HITL Workflow (Мягкое вмешательство)

```python
# В BESSER Agent интеграция

@write_letter_state.body
def review_draft(session):
    """После того как пользователь написал письмо"""
    
    draft = session.memory.get("draft")
    child_age = session.memory.get("child_age")
    
    # Анализ через Guardian Agent
    guardian = ContentGuardianAgent()
    review = guardian.review_letter(
        user_id=session.user_id,
        letter_text=draft,
        child_age=child_age,
        context=session.memory.get_all()
    )
    
    intervention = review["intervention"]
    
    if intervention["level"] == "none":
        # Все хорошо
        session.reply(intervention["message"])
        session.reply("""
        Сохранить письмо?
        1. ✅ Да, сохранить
        2. ✏️ Хочу еще отредактировать
        """)
        return save_letter_state
    
    elif intervention["level"] == "gentle_nudge":
        # Мягкое предложение
        session.reply(intervention["message"])
        
        # Показать альтернативы
        suggestions = review["rewritten_suggestions"]
        session.reply(f"""
        Предлагаю альтернативу:
        
        ───────────────────
        {suggestions["short_version"]}
        ───────────────────
        
        Что изменилось:
        {chr(10).join(f"• {change}" for change in suggestions["key_changes"])}
        
        Выберите:
        1. ✅ Использовать мою версию
        2. 📝 Использовать предложенную
        3. ✏️ Отредактировать самому
        4. 💾 Сохранить как черновик (вернуться позже)
        """)
        
        session.memory.set("review_suggestions", suggestions)
        return letter_decision_state
    
    else:  # strong_recommendation
        # Серьезная рекомендация, но не блокировка
        session.reply(intervention["message"])
        
        # Показать обе версии рядом
        suggestions = review["rewritten_suggestions"]
        session.reply(f"""
        ┌─ ИСХОДНАЯ ВЕРСИЯ ─────────────────────┐
        {draft}
        └───────────────────────────────────────┘
        
        ┌─ ПРЕДЛОЖЕННАЯ ВЕРСИЯ ─────────────────┐
        {suggestions["long_version"]}
        └───────────────────────────────────────┘
        
        Я настоятельно рекомендую использовать вторую версию.
        
        Но решение за вами:
        1. 📝 Использовать рекомендованную версию
        2. ✏️ Отредактировать исходную с моей помощью
        3. 💾 Сохранить исходную как черновик
        4. ⚠️ Все равно сохранить исходную (не рекомендуется)
        """)
        
        # Если выберет #4, пометить для follow-up
        if intervention.get("flag_for_followup"):
            session.memory.set("flagged_letter_id", draft_id)
        
        return letter_decision_state


@letter_decision_state.body
def handle_decision(session):
    choice = session.message
    
    if "рекомендованную" in choice or choice == "1":
        # Приняли предложение
        suggestions = session.memory.get("review_suggestions")
        final_text = suggestions["long_version"]
        
        session.reply("✅ Отличный выбор! Это письмо будет исцеляющим для ребенка.")
        
        # Сохранить с меткой "reviewed_and_improved"
        save_letter(session.user_id, final_text, metadata={
            "guardian_review": "passed_with_improvements",
            "original_had_issues": True
        })
        
    elif "исходную" in choice and "равно" in choice:
        # Проигнорировал рекомендацию
        original = session.memory.get("draft")
        
        session.reply("""
        Хорошо, я сохраню ваш вариант.
        
        Но помните: это письмо предназначено для ребенка, который 
        может прочитать его через годы. Убедитесь, что оно показывает 
        вашу любовь, а не боль.
        
        Возможно, через какое-то время вы захотите вернуться к нему?
        """)
        
        # Сохранить с warning flag
        letter_id = save_letter(session.user_id, original, metadata={
            "guardian_review": "warning_ignored",
            "needs_followup": True,
            "followup_date": datetime.now() + timedelta(days=7)
        })
        
        # Запланировать follow-up
        schedule_followup(session.user_id, letter_id, days=7)
    
    elif "черновик" in choice:
        # Отложить решение
        draft_id = save_draft(session.user_id, session.memory.get("draft"))
        
        session.reply("""
        💾 Сохранено как черновик.
        
        Хорошее решение дать себе время подумать.
        Иногда эмоции должны остыть, чтобы слова стали исцеляющими.
        
        Вернуться к черновикам: /drafts
        """)
```

---

## 🔄 Follow-up System (возврат к проблемным письмам)

```python
class FollowUpManager:
    """Система отложенных возвратов к проблемным письмам"""
    
    def __init__(self, kag_client):
        self.kag = kag_client
    
    def schedule_followup(
        self, 
        user_id: str, 
        letter_id: str, 
        days: int = 7
    ):
        """Запланировать возврат к письму"""
        
        self.kag.create_node(
            type="FollowUp",
            properties={
                "user_id": user_id,
                "letter_id": letter_id,
                "scheduled_date": datetime.now() + timedelta(days=days),
                "reason": "warning_ignored",
                "status": "pending"
            }
        )
    
    def check_due_followups(self, user_id: str) -> list:
        """Проверить просроченные follow-ups"""
        
        followups = self.kag.query(f"""
        MATCH (f:FollowUp)-[:REFERS_TO]->(l:Letter)
        WHERE f.user_id = '{user_id}'
        AND f.scheduled_date <= datetime()
        AND f.status = 'pending'
        RETURN f, l
        """)
        
        return followups
    
    def initiate_followup_conversation(
        self, 
        session, 
        letter_id: str
    ):
        """Инициировать разговор о проблемном письме"""
        
        # Получить письмо
        letter = self.kag.get_node(letter_id)
        
        # Мягкое начало
        session.reply("""
        Привет! Помните, неделю назад вы написали письмо ребенку?
        
        Я хотел вернуться к нему, если вы не против.
        """)
        
        # Через паузу
        time.sleep(2)
        
        session.reply(f"""
        Вот то письмо:
        
        ───────────────────
        {letter['content'][:200]}...
        ───────────────────
        
        Тогда я высказал опасения по поводу некоторых формулировок.
        
        Сейчас, когда прошло время, как вы сами относитесь к этому письму?
        Может, хотите что-то изменить?
        """)
        
        # Дать пользователю высказаться
        # ...
        
        session.reply("""
        Предлагаю вместе его переработать. Не потому что исходный 
        вариант "плохой", а потому что мы можем сделать его еще более 
        исцеляющим для ребенка.
        
        Согласны?
        """)


# Интеграция в бота
@scheduler.daily(hour=19)  # Вечером, когда спокойнее
def run_followup_check():
    """Ежедневная проверка follow-ups"""
    
    active_users = get_active_users()
    followup_manager = FollowUpManager(kag)
    
    for user_id in active_users:
        due_followups = followup_manager.check_due_followups(user_id)
        
        if due_followups:
            # Отправить мягкое напоминание
            send_message(user_id, """
            👋 Привет! Есть пара моментов, о которых хотел поговорить.
            Когда будет удобно?
            """)
            
            # Когда ответит, инициировать follow-up
            # ...
```

---

## 🔧 Интерфейс для проверки сообщений

### **1. Inline проверка в Telegram**

```python
@therapy_agent.command("/check")
def check_message_interface(session):
    """Интерфейс проверки сообщений"""
    
    session.reply("""
    ✉️ ПРОВЕРКА СООБЩЕНИЙ
    
    Я помогу вам проверить сообщение перед отправкой.
    
    Что хотите проверить?
    1. 📤 Мое сообщение бывшему партнеру
    2. 📥 Сообщение от бывшего партнера (анализ)
    3. 💌 Письмо ребенку
    """)
    
    return check_mode_select_state

@check_mode_select_state.body
def select_check_mode(session):
    choice = session.message
    
    if "бывшему" in choice or choice == "1":
        session.reply("""
        Напишите или перешлите сообщение, которое хотите отправить 
        бывшему партнеру. Я проверю его на:
        
        • Тон и токсичность
        • Манипуляции
        • Соответствие BIFF-принципам
        • Риск эскалации конфликта
        
        А затем предложу улучшения, если нужно.
        """)
        session.memory.set("check_mode", "outgoing_to_ex")
        return analyze_message_state
        
    elif "от бывшего" in choice or choice == "2":
        session.reply("""
        Перешлите мне сообщение от вашего бывшего партнера.
        
        Я помогу вам:
        • Распознать манипулятивные техники
        • Понять скрытые намерения
        • Выработать стратегию ответа
        • Не попасть в эмоциональную ловушку
        """)
        session.memory.set("check_mode", "incoming_from_ex")
        return analyze_message_state
        
    elif "ребенку" in choice or choice == "3":
        # Уже есть в workflow написания письма
        pass


@analyze_message_state.body
def analyze_and_respond(session):
    """Анализ и предоставление обратной связи"""
    
    message_text = session.message
    check_mode = session.memory.get("check_mode")
    guardian = ContentGuardianAgent()
    
    if check_mode == "outgoing_to_ex":
        # Проверка сообщения бывшему
        review = guardian.review_message_to_ex(
            session.user_id,
            message_text
        )
        
        # Форматировать результат
        response = "📊 АНАЛИЗ ВАШЕГО СООБЩЕНИЯ\n\n"
        
        # Toxicity
        toxicity = review["analysis"]["toxicity"]
        response += f"🌡 Тон: {get_tone_emoji(toxicity['toxicity_score'])} "
        response += f"({toxicity['severity']})\n"
        
        # BIFF compliance
        biff = review["analysis"]["biff_compliance"]
        response += f"\n📋 BIFF-совместимость:\n"
        for criterion, passed in biff.items():
            response += f"{'✅' if passed else '❌'} {criterion}\n"
        
        # Escalation risk
        escalation = review["analysis"]["escalation_risk"]
        response += f"\n⚠️ Риск эскалации: {escalation['level']}\n"
        
        if review["intervention"]["level"] != "none":
            response += f"\n{review['intervention']['message']}\n"
            
            # Показать улучшенную версию
            suggestions = review["rewritten_suggestions"]
            response += f"""
            
            💡 ПРЕДЛОЖЕННАЯ ВЕРСИЯ:
            ───────────────────
            {suggestions['biff_version']}
            ───────────────────
            
            Что изменилось:
            {chr(10).join(f"• {change}" for change in suggestions['improvements'])}
            
            Использовать эту версию?
            1. ✅ Да, скопировать
            2. ✏️ Доработать вместе
            3. ❌ Нет, отправлю свою
            """
        
        session.reply(response)
        
    elif check_mode == "incoming_from_ex":
        # Анализ входящего сообщения
        analysis = guardian.analyze_incoming_message(
            session.user_id,
            message_text
        )
        
        response = "🔍 АНАЛИЗ СООБЩЕНИЯ ОТ БЫВШЕГО ПАРТНЕРА\n\n"
        
        # Toxicity
        toxicity = analysis["analysis"]["toxicity"]
        response += f"🌡 Токсичность: {toxicity['severity']}\n"
        
        # Manipulation tactics
        manipulation = analysis["analysis"]["manipulation"]
        if manipulation["has_manipulation"]:
            response += f"\n⚠️ ОБНАРУЖЕНЫ МАНИПУЛЯЦИИ:\n\n"
            response += analysis["breakdown"]["explanation"]
            response += "\n\n"
            
            for tactic in manipulation["types"]:
                response += f"🎭 {tactic}:\n"
                response += f"   {get_tactic_explanation(tactic)}\n\n"
        
        # Response guidance
        guidance = analysis["response_guidance"]
        response += f"""
        
        💡 КАК ОТВЕТИТЬ:
        
        {guidance['strategy']}
        
        Предлагаемый ответ:
        ───────────────────
        {guidance['suggested_response']}
        ───────────────────
        
        Хотите:
        1. 📋 Скопировать предложенный ответ
        2. ✏️ Написать свой с моей помощью
        3. 🚫 Не отвечать (иногда это лучший вариант)
        """
        
        session.reply(response)
```

### **2. Web Dashboard (опционально)**

Для более визуального интерфейса можно создать mini-app:

```javascript
// React компонент для анализа сообщений

function MessageChecker() {
  const [message, setMessage] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [mode, setMode] = useState('outgoing'); // outgoing / incoming
  
  const analyzeMessage = async () => {
    const response = await fetch('/api/guardian/analyze', {
      method: 'POST',
      body: JSON.stringify({ message, mode })
    });
    const result = await response.json();
    setAnalysis(result);
  };
  
  return (
    <div className="message-checker">
      <div className="mode-selector">
        <button onClick={() => setMode('outgoing')}>
          Моё сообщение бывшему
        </button>
        <button onClick={() => setMode('incoming')}>
          Сообщение от бывшего
        </button>
      </div>
      
      <textarea 
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Вставьте сообщение для анализа..."
      />
      
      <button onClick={analyzeMessage}>
        Проверить
      </button>
      
      {analysis && (
        <AnalysisResults 
          data={analysis} 
          mode={mode}
        />
      )}
    </div>
  );
}

function AnalysisResults({ data, mode }) {
  return (
    <div className="analysis-results">
      {/* Toxicity meter */}
      <ToxicityMeter score={data.toxicity.score} />
      
      {/* Flags */}
      <FlagsList flags={data.flags} />
      
      {/* Suggestions */}
      {data.suggestions && (
        <div className="suggestions">
          <h3>💡 Предложения</h3>
          <ComparisonView 
            original={data.original}
            suggested={data.suggestions.rewritten}
            changes={data.suggestions.changes}
          />
        </div>
      )}
      
      {/* Manipulation breakdown (for incoming) */}
      {mode === 'incoming' && data.manipulation && (
        <ManipulationBreakdown data={data.manipulation} />
      )}
    </div>
  );
}
```

---

## 📊 Pattern Tracking в KAG

```python
# Отслеживание динамики пользователя

kag.query(f"""
MATCH (u:User {{id: '{user_id}'}})-[:WROTE]->(l:Letter)
-[:HAD_REVIEW]->(r:GuardianReview)
WHERE r.date > date('2024-01-01')
RETURN 
  r.date,
  r.toxicity_score,
  r.issues_found,
  r.user_accepted_suggestions
ORDER BY r.date
""")

# Визуализация прогресса пользователя
def show_progress_chart(session):
    user_id = session.user_id
    
    # Получить историю проверок
    reviews = kag.get_user_review_history(user_id)
    
    # Построить график
    chart = create_progress_chart(reviews)
    
    session.reply(f"""
    📈 ВАШ ПРОГРЕСС
    
    За последние 3 месяца:
    
    {chart}
    
    ✅ Положительные изменения:
    • Токсичность снизилась на 60%
    • Вы стали чаще принимать рекомендации
    • В последних 5 письмах не было упоминаний другого родителя
    
    Это огромный прогресс! Вы учитесь писать исцеляюще.
    """)
```

---

## ✅ Итоговая рекомендация

**Архитектура:**

```
BESSER Agent (Workflow) 
    ↓
Content Guardian Agent (Analysis)
    ├→ Toxicity Analyzer (Detoxify + Rules)
    ├→ Manipulation Detector (Patterns + LLM)
    ├→ Child Safety Validator (LLM holistic)
    └→ BIFF Checker
    ↓
HITL Decision Point (Soft Intervention)
    ↓
KAG (Pattern Tracking + Follow-ups)
```

**Интерфейс:**
- Telegram inline для быстрой проверки
- Mini-app для визуального dashboard (опционально)
- Автоматические follow-ups через бота

**Ключевые принципы:**
1. ✅ **Не блокировать** — всегда давать выбор
2. 📚 **Обучать** — объяснять почему это проблема
3. 💡 **Предлагать альтернативы** — конкретные rewrites
4. 🔄 **Возвращаться** — follow-up к проигнорированным warning
5. 📈 **Показывать прогресс** — мотивация через визуализацию роста

Нужна детальная реализация какого-то конкретного компонента? Например, полный код ManipulationDetector или интерфейс follow-up conversation?