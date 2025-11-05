"""NVC (Nonviolent Communication) transformer for letters."""

from typing import Dict, Any, List
from dataclasses import dataclass

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class NVCStructure:
    """NVC four-part structure."""
    observation: str  # Objective facts
    feeling: str      # Emotions
    need: str         # Underlying needs
    request: str      # Specific request


class NVCTransformer:
    """Transform letters to Nonviolent Communication (NVC) format."""

    def transform(self, letter_text: str) -> Dict[str, Any]:
        """Transform letter to NVC structure."""

        nvc_template = """
Привет [Имя],

**Наблюдение:** [Конкретные факты без оценок]
Когда {observation},

**Чувство:** [Ваши эмоции]
Я чувствую {feeling},

**Потребность:** [Что важно для вас]
Потому что мне важно {need}.

**Просьба:** [Конкретная просьба]
Был бы благодарен, если бы {request}.

Спасибо за понимание,
[Ваше имя]
"""

        return {
            "original_text": letter_text,
            "nvc_template": nvc_template.strip(),
            "structure": NVCStructure(
                observation="[когда случается X]",
                feeling="[я чувствую Y]",
                need="[потому что мне нужно Z]",
                request="[пожалуйста сделай W]"
            )
        }
