"""Simple regex-based PII protection.

Lightweight alternative to Presidio for PII detection and masking.
Handles common PII patterns without heavy ML dependencies.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from src.core.logger import get_logger


logger = get_logger(__name__)


@dataclass
class PIIMatch:
    """Detected PII match."""
    entity_type: str
    start: int
    end: int
    text: str
    confidence: float = 1.0


class SimplePIIProtector:
    """Simple regex-based PII detector and masker."""

    # Email pattern (RFC 5322 simplified)
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        re.IGNORECASE
    )

    # Phone patterns (Russian and international)
    PHONE_PATTERNS = [
        # Russian: +7 (999) 123-45-67, 8-800-555-35-35
        re.compile(r'(?:\+7|8)[\s\-]?(?:\(?\d{3}\)?[\s\-]?)?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'),
        # International: +1-234-567-8900
        re.compile(r'\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9}'),
        # Simple: 1234567890 (10+ digits)
        re.compile(r'\b\d{10,}\b'),
    ]

    # Credit card pattern (basic)
    CREDIT_CARD_PATTERN = re.compile(
        r'\b(?:\d{4}[\s\-]?){3}\d{4}\b'
    )

    # Russian passport pattern: 1234 567890
    PASSPORT_PATTERN = re.compile(
        r'\b\d{4}\s?\d{6}\b'
    )

    # SNILS pattern: 123-456-789 01
    SNILS_PATTERN = re.compile(
        r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}\b'
    )

    # Common Russian names (subset for demo - в production добавить полный список)
    COMMON_RUSSIAN_NAMES = {
        # Male names
        'александр', 'дмитрий', 'максим', 'сергей', 'андрей', 'алексей',
        'артём', 'илья', 'кирилл', 'михаил', 'никита', 'матвей', 'иван',
        'егор', 'арсений', 'павел', 'роман', 'ярослав', 'тимофей', 'даниил',
        # Female names
        'анна', 'мария', 'елена', 'ольга', 'татьяна', 'наталья', 'ирина',
        'екатерина', 'светлана', 'людмила', 'алиса', 'виктория', 'полина',
        'дарья', 'анастасия', 'валерия', 'ксения', 'юлия', 'марина', 'вера',
        # Common short forms
        'саша', 'дима', 'макс', 'серёжа', 'лёша', 'женя', 'коля', 'петя',
        'вова', 'лена', 'катя', 'наташа', 'оля', 'таня', 'маша', 'даша'
    }

    def __init__(self):
        """Initialize PII protector."""
        self.enabled = True
        logger.info("simple_pii_protector_initialized", mode="regex-based")

    def detect(self, text: str) -> List[PIIMatch]:
        """
        Detect PII entities in text.

        Args:
            text: Input text

        Returns:
            List of detected PII matches
        """
        if not self.enabled:
            return []

        matches = []

        # Detect emails
        for match in self.EMAIL_PATTERN.finditer(text):
            matches.append(PIIMatch(
                entity_type="EMAIL",
                start=match.start(),
                end=match.end(),
                text=match.group(),
                confidence=0.95
            ))

        # Detect phone numbers
        for pattern in self.PHONE_PATTERNS:
            for match in pattern.finditer(text):
                # Skip if already detected
                if not any(m.start <= match.start() < m.end for m in matches):
                    matches.append(PIIMatch(
                        entity_type="PHONE",
                        start=match.start(),
                        end=match.end(),
                        text=match.group(),
                        confidence=0.85
                    ))

        # Detect credit cards
        for match in self.CREDIT_CARD_PATTERN.finditer(text):
            matches.append(PIIMatch(
                entity_type="CREDIT_CARD",
                start=match.start(),
                end=match.end(),
                text=match.group(),
                confidence=0.90
            ))

        # Detect Russian passports
        for match in self.PASSPORT_PATTERN.finditer(text):
            matches.append(PIIMatch(
                entity_type="PASSPORT",
                start=match.start(),
                end=match.end(),
                text=match.group(),
                confidence=0.80
            ))

        # Detect SNILS
        for match in self.SNILS_PATTERN.finditer(text):
            matches.append(PIIMatch(
                entity_type="SNILS",
                start=match.start(),
                end=match.end(),
                text=match.group(),
                confidence=0.85
            ))

        # Detect common Russian names (case-insensitive)
        words = re.finditer(r'\b\w+\b', text, re.UNICODE)
        for match in words:
            word = match.group().lower()
            if word in self.COMMON_RUSSIAN_NAMES:
                # Skip if already detected as other PII
                if not any(m.start <= match.start() < m.end for m in matches):
                    matches.append(PIIMatch(
                        entity_type="PERSON_NAME",
                        start=match.start(),
                        end=match.end(),
                        text=match.group(),
                        confidence=0.70  # Lower confidence for names
                    ))

        # Sort by position
        matches.sort(key=lambda m: m.start)

        return matches

    def anonymize(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
        mask_char: str = "*"
    ) -> str:
        """
        Anonymize PII in text by masking.

        Args:
            text: Input text
            entity_types: Specific entity types to mask (None = all)
            mask_char: Character to use for masking

        Returns:
            Anonymized text
        """
        matches = self.detect(text)

        # Filter by entity types if specified
        if entity_types:
            matches = [m for m in matches if m.entity_type in entity_types]

        # No matches - return original
        if not matches:
            return text

        # Build anonymized text
        result = []
        last_end = 0

        for match in matches:
            # Add text before match
            result.append(text[last_end:match.start])

            # Add masked entity
            mask = self._get_mask(match, mask_char)
            result.append(mask)

            last_end = match.end

        # Add remaining text
        result.append(text[last_end:])

        return ''.join(result)

    def _get_mask(self, match: PIIMatch, mask_char: str) -> str:
        """
        Get appropriate mask for entity type.

        Args:
            match: PII match
            mask_char: Mask character

        Returns:
            Masked string
        """
        entity_type = match.entity_type

        if entity_type == "EMAIL":
            # Mask email but keep domain: user@example.com -> ****@example.com
            parts = match.text.split('@')
            if len(parts) == 2:
                return f"{mask_char * 4}@{parts[1]}"
            return mask_char * len(match.text)

        elif entity_type == "PHONE":
            # Mask phone but keep last 2 digits: +7-999-123-45-67 -> ***-**-67
            if len(match.text) >= 2:
                return f"{mask_char * (len(match.text) - 2)}{match.text[-2:]}"
            return mask_char * len(match.text)

        elif entity_type == "CREDIT_CARD":
            # Mask all but last 4 digits: 1234-5678-9012-3456 -> ****-****-****-3456
            digits = ''.join(c for c in match.text if c.isdigit())
            if len(digits) >= 4:
                masked_digits = f"{mask_char * (len(digits) - 4)}{digits[-4:]}"
                # Reconstruct with original separators
                result = masked_digits
                for i, c in enumerate(match.text):
                    if not c.isdigit():
                        result = result[:i] + c + result[i:]
                return result[:len(match.text)]
            return mask_char * len(match.text)

        elif entity_type == "PERSON_NAME":
            # Mask names partially: Александр -> А********
            if len(match.text) > 1:
                return f"{match.text[0]}{mask_char * (len(match.text) - 1)}"
            return mask_char

        else:
            # Default: full masking
            return mask_char * len(match.text)

    def get_statistics(self, text: str) -> Dict[str, int]:
        """
        Get PII detection statistics.

        Args:
            text: Input text

        Returns:
            Dictionary with entity type counts
        """
        matches = self.detect(text)

        stats = {}
        for match in matches:
            entity_type = match.entity_type
            stats[entity_type] = stats.get(entity_type, 0) + 1

        return stats
