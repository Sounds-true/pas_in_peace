"""Safety planning module for crisis management."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json

from src.core.logger import get_logger


logger = get_logger(__name__)


@dataclass
class SafetyPlan:
    """User's personalized safety plan."""
    plan_id: str
    user_id: str
    warning_signs: List[str]
    coping_strategies: List[str]
    reasons_for_living: List[str]
    safe_people: List[Dict[str, str]]  # [{"name": "...", "phone": "..."}]
    safe_places: List[str]
    professional_contacts: List[Dict[str, str]]  # [{"name": "...", "phone": "..."}]
    crisis_hotlines: List[Dict[str, str]]  # [{"name": "...", "phone": "...", "available": "..."}]
    making_environment_safe: List[str]  # Remove means
    created_at: datetime
    updated_at: datetime
    active: bool


@dataclass
class SafetyContract:
    """Safety contract between user and support system."""
    contract_id: str
    user_id: str
    contract_text: str
    user_commitment: str
    signed_at: datetime
    expires_at: Optional[datetime]
    active: bool


class SafetyPlanner:
    """
    Manages safety plans and contracts.

    Implements evidence-based safety planning:
    - Warning signs identification
    - Coping strategies development
    - Support network activation
    - Environmental safety measures

    Based on:
    - Stanley & Brown (2012) Safety Planning Intervention
    - SAFE-T protocol
    """

    def __init__(self):
        """Initialize safety planner."""
        # Default crisis hotlines (Russia)
        self.default_hotlines = [
            {
                "name": "Всероссийская линия помощи",
                "phone": "8-800-2000-122",
                "available": "24/7",
                "language": "russian",
                "description": "Бесплатная анонимная психологическая помощь"
            },
            {
                "name": "Телефон доверия для детей и подростков",
                "phone": "8-800-2000-122",
                "available": "24/7",
                "language": "russian",
                "description": "Помощь детям, подросткам и родителям"
            },
            {
                "name": "Экстренная психологическая помощь МЧС",
                "phone": "8-495-989-5050",
                "available": "24/7",
                "language": "russian",
                "description": "Кризисная психологическая помощь"
            },
            {
                "name": "International Association for Suicide Prevention",
                "phone": "various",
                "available": "24/7",
                "language": "multilingual",
                "description": "befrienders.org for global crisis lines"
            }
        ]

        # Default coping strategies
        self.default_coping_strategies = {
            "russian": [
                "Техника дыхания 4-7-8 (вдох 4 сек, задержка 7 сек, выдох 8 сек)",
                "Прогулка на свежем воздухе (15-30 минут)",
                "Звонок другу или близкому человеку",
                "Прослушивание успокаивающей музыки",
                "Техника заземления: назвать 5 вещей, которые вижу, 4 - которые слышу, 3 - которые ощущаю",
                "Теплый душ или ванна",
                "Физическая активность (йога, растяжка, пробежка)",
                "Ведение дневника (выписывание мыслей и чувств)",
                "Чтение книги или просмотр успокаивающего фильма",
                "Обращение к специалисту (психолог, психотерапевт)"
            ],
            "english": [
                "4-7-8 breathing technique (inhale 4s, hold 7s, exhale 8s)",
                "Walk outside (15-30 minutes)",
                "Call a friend or loved one",
                "Listen to calming music",
                "Grounding: name 5 things I see, 4 I hear, 3 I feel",
                "Warm shower or bath",
                "Physical activity (yoga, stretching, jogging)",
                "Journaling (write down thoughts and feelings)",
                "Read a book or watch a calming movie",
                "Contact a mental health professional"
            ]
        }

    async def create_safety_plan(
        self,
        user_id: str,
        warning_signs: List[str],
        coping_strategies: List[str],
        reasons_for_living: List[str],
        safe_people: List[Dict[str, str]],
        safe_places: List[str],
        professional_contacts: Optional[List[Dict[str, str]]] = None,
        making_environment_safe: Optional[List[str]] = None
    ) -> SafetyPlan:
        """
        Create a personalized safety plan.

        Args:
            user_id: User identifier
            warning_signs: Early warning signs of crisis
            coping_strategies: User's coping strategies
            reasons_for_living: Reasons to keep living
            safe_people: Trusted people to contact
            safe_places: Safe environments
            professional_contacts: Mental health professionals
            making_environment_safe: Steps to remove means

        Returns:
            SafetyPlan object
        """
        plan_id = str(uuid.uuid4())
        now = datetime.now()

        # Add default hotlines
        crisis_hotlines = self.default_hotlines.copy()

        # Merge with any custom professional contacts
        if professional_contacts is None:
            professional_contacts = []

        # Default environment safety steps
        if making_environment_safe is None:
            making_environment_safe = [
                "Убрать опасные предметы (лекарства, оружие, острые предметы)",
                "Попросить близкого человека хранить опасные предметы",
                "Установить приложение для блокировки опасного контента",
                "Договориться с кем-то о ежедневных проверках"
            ]

        plan = SafetyPlan(
            plan_id=plan_id,
            user_id=user_id,
            warning_signs=warning_signs,
            coping_strategies=coping_strategies,
            reasons_for_living=reasons_for_living,
            safe_people=safe_people,
            safe_places=safe_places,
            professional_contacts=professional_contacts,
            crisis_hotlines=crisis_hotlines,
            making_environment_safe=making_environment_safe,
            created_at=now,
            updated_at=now,
            active=True
        )

        logger.info(
            "safety_plan_created",
            plan_id=plan_id,
            user_id=user_id,
            warning_signs_count=len(warning_signs),
            coping_strategies_count=len(coping_strategies),
            safe_people_count=len(safe_people)
        )

        # TODO: Save to database
        # await self._save_to_db(plan)

        return plan

    async def create_safety_contract(
        self,
        user_id: str,
        commitment_type: str = "no_harm"
    ) -> SafetyContract:
        """
        Create a safety contract.

        Args:
            user_id: User identifier
            commitment_type: Type of commitment ("no_harm", "seek_help")

        Returns:
            SafetyContract object
        """
        contract_id = str(uuid.uuid4())
        now = datetime.now()

        # Contract templates
        contracts = {
            "no_harm": {
                "russian": """
Я, {user_id}, обещаю:

1. Если у меня появятся мысли о причинении вреда себе, я немедленно обращусь за помощью.

2. Я позвоню на кризисную линию (8-800-2000-122) или близкому человеку.

3. Я не буду предпринимать действий без обращения за помощью.

4. Я понимаю, что эти чувства временны, и есть люди, готовые мне помочь.

5. Я буду следовать моему плану безопасности.

Я даю это обещание себе и тем, кто меня поддерживает.
                """,
                "english": """
I, {user_id}, promise:

1. If I have thoughts of harming myself, I will immediately seek help.

2. I will call a crisis line or trusted person.

3. I will not take action without seeking help first.

4. I understand these feelings are temporary, and people are ready to help me.

5. I will follow my safety plan.

I make this promise to myself and those who support me.
                """
            },
            "seek_help": {
                "russian": """
Я обещаю обращаться за помощью, если:

- Мои мысли о суициде усиливаются
- Я начинаю планировать действия
- Я чувствую, что теряю контроль
- Мои предупреждающие знаки активируются

Я позвоню: [список контактов из плана безопасности]

Я понимаю, что обращение за помощью - это проявление силы, а не слабости.
                """,
                "english": """
I promise to seek help if:

- My suicidal thoughts intensify
- I start planning actions
- I feel I'm losing control
- My warning signs activate

I will call: [contacts from safety plan]

I understand seeking help is a sign of strength, not weakness.
                """
            }
        }

        # Select contract (default Russian)
        contract_text = contracts.get(commitment_type, contracts["no_harm"])["russian"]

        contract = SafetyContract(
            contract_id=contract_id,
            user_id=user_id,
            contract_text=contract_text,
            user_commitment=f"Я принимаю условия контракта безопасности {commitment_type}",
            signed_at=now,
            expires_at=None,  # No expiration by default
            active=True
        )

        logger.info(
            "safety_contract_created",
            contract_id=contract_id,
            user_id=user_id,
            commitment_type=commitment_type
        )

        # TODO: Save to database
        # await self._save_to_db(contract)

        return contract

    async def retrieve_safety_plan(self, user_id: str) -> Optional[SafetyPlan]:
        """
        Retrieve user's active safety plan.

        Args:
            user_id: User identifier

        Returns:
            SafetyPlan if exists, None otherwise
        """
        # TODO: Retrieve from database
        logger.info("safety_plan_retrieved", user_id=user_id)
        return None

    async def update_safety_plan(
        self,
        plan_id: str,
        updates: Dict[str, Any]
    ) -> SafetyPlan:
        """
        Update existing safety plan.

        Args:
            plan_id: Safety plan ID
            updates: Fields to update

        Returns:
            Updated SafetyPlan
        """
        # TODO: Update in database
        updates["updated_at"] = datetime.now()
        logger.info("safety_plan_updated", plan_id=plan_id, fields=list(updates.keys()))
        raise NotImplementedError("Database integration pending")

    async def deactivate_safety_plan(self, plan_id: str) -> bool:
        """
        Deactivate a safety plan.

        Args:
            plan_id: Safety plan ID

        Returns:
            True if successful
        """
        # TODO: Update in database
        logger.info("safety_plan_deactivated", plan_id=plan_id)
        return True

    def get_default_coping_strategies(self, language: str = "russian") -> List[str]:
        """Get default coping strategies."""
        return self.default_coping_strategies.get(language, self.default_coping_strategies["russian"])

    def get_crisis_hotlines(self, country: str = "russia") -> List[Dict[str, str]]:
        """Get crisis hotlines for a country."""
        # For now, return default (Russia)
        return self.default_hotlines
