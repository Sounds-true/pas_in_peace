"""Guided letter writing system (Legacy - use EnhancedLetterWriter for new code)."""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.letters.types import LetterStage  # Import from types.py to avoid duplication
from src.letters.biff_transformer import BIFFTransformer
from src.letters.nvc_transformer import NVCTransformer
from src.letters.validator import LetterValidator
from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LetterSession:
    """Letter writing session state."""
    user_id: str
    stage: LetterStage
    purpose: str  # schedule_change, information_request, boundary
    style: str  # biff or nvc
    draft: str = ""
    transformed: str = ""
    is_complete: bool = False


class LetterWriter:
    """Guided letter writing with BIFF/NVC transformation."""

    def __init__(self):
        """Initialize letter writer."""
        self.biff = BIFFTransformer()
        self.nvc = NVCTransformer()
        self.validator = LetterValidator()
        self.sessions: Dict[str, LetterSession] = {}

    async def start_letter(
        self,
        user_id: str,
        purpose: str = "information_request",
        style: str = "biff"
    ) -> str:
        """
        Start guided letter writing session.

        Args:
            user_id: User ID
            purpose: Letter purpose
            style: biff or nvc

        Returns:
            Guidance message
        """
        session = LetterSession(
            user_id=user_id,
            stage=LetterStage.INIT,
            purpose=purpose,
            style=style
        )
        self.sessions[user_id] = session

        if style == "biff":
            template = self.biff.get_biff_template(purpose)
            guidance = f"""
📝 **Начинаем письмо (BIFF стиль)**

Принципы BIFF:
• Brief (Кратко) - не более 200 слов
• Informative (Информативно) - конкретные факты
• Friendly (Дружелюбно) - вежливый тон
• Firm (Твёрдо) - чёткие границы

**Шаблон:**
{template}

Напишите ваш черновик, заполнив [скобки].
"""
        else:
            nvc_info = self.nvc.transform("")
            guidance = f"""
📝 **Начинаем письмо (NVC стиль)**

Структура NVC:
1. Наблюдение (факты)
2. Чувство (эмоции)
3. Потребность (что важно)
4. Просьба (конкретная)

**Шаблон:**
{nvc_info['nvc_template']}

Напишите ваш черновик.
"""

        session.stage = LetterStage.DRAFT
        return guidance

    async def process_draft(self, user_id: str, draft_text: str) -> Dict[str, Any]:
        """
        Process user's letter draft.

        Args:
            user_id: User ID
            draft_text: Draft letter text

        Returns:
            Processing results with transformed letter
        """
        session = self.sessions.get(user_id)
        if not session:
            return {"error": "No active letter session"}

        session.draft = draft_text
        session.stage = LetterStage.TRANSFORM

        # Transform based on style
        if session.style == "biff":
            result = self.biff.transform(draft_text)
            transformed = result["transformed_text"]
            analysis = result["final_analysis"]

            response = f"""
✅ **Анализ письма (BIFF)**

**Оценка:** {analysis.score * 100:.0f}%
- Brief: {"✅" if analysis.is_brief else "❌"} ({analysis.word_count} слов)
- Informative: {"✅" if analysis.is_informative else "❌"}
- Friendly: {"✅" if analysis.is_friendly else "❌"}
- Firm: {"✅" if analysis.is_firm else "❌"}

**Трансформированный вариант:**
{transformed}

**Рекомендации:**
{chr(10).join(f"• {s}" for s in result["suggestions"])}

Хотите использовать это письмо? (да/нет/редактировать)
"""
        else:
            result = self.nvc.transform(draft_text)
            transformed = result["nvc_template"]
            response = f"""
✅ **Структура NVC**

{transformed}

Заполните структуру на основе вашего черновика.
"""

        session.transformed = transformed
        session.stage = LetterStage.VALIDATE

        return {
            "response": response,
            "transformed": transformed,
            "result": result
        }

    async def finalize_letter(self, user_id: str) -> str:
        """Finalize letter and provide final version."""
        session = self.sessions.get(user_id)
        if not session:
            return "Нет активной сессии письма"

        # Validate
        validation = self.validator.validate(session.transformed)

        if not validation["is_safe"]:
            return f"""
⚠️ **Требуется доработка**

Проблемы:
{chr(10).join(f"• {i}" for i in validation["issues"])}

Предупреждения:
{chr(10).join(f"• {w}" for w in validation["warnings"])}

Пожалуйста, исправьте и отправьте снова.
"""

        session.is_complete = True
        session.stage = LetterStage.FINALIZE

        return f"""
✅ **Письмо готово!**

**Финальная версия:**

{session.transformed}

**Рекомендации перед отправкой:**
• Перечитайте через несколько часов
• Покажите другу для обратной связи
• Отправляйте когда спокойны
• Сохраните копию для себя

Удачи! 🍀
"""
